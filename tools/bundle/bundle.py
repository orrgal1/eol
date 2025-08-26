#!/usr/bin/env python3
"""
bundle.py — zero-dependency bundler

Repo layout:
  <story>/<book>/<lang>/<subject>/<item>.md
  Example: eol_saga/book1/english/chapters/chapter-001.md
  
  Characters have nested structure:
  <story>/<book>/<lang>/characters/<character>/<state>.md
  Example: eol_saga/book1/english/characters/brenden/farmboy.md

Supports:
- Ranges: foo-001..010
- Globs: *, ?, [0-9]
- Multiple subjects in one run
- Character patterns: "brenden", "brenden/farmboy", "*/farmboy", "brenden/*", "*/*"
- Flexible subject:item configurations
- Flat output mode
- Outputs a directory and prints a manifest (paths relative to --base-dir)

Flags:
  --story       Story folder (e.g., eol_saga)
  --book        Book folder (e.g., book1)
  --lang        Language folder (default: english)
  --subjects    Flexible subject:item configurations (e.g., "chapters:000..004,characters:brenden")
  --flat        Flatten output structure (default: false)
  --extension   Default extension to append (default: .md)
  --output      Output directory path (default: tools/bundle/bundles/story_bundle)
  --base-dir    Repo root (default: current directory)

Examples:
  # Get specific items
  python bundle.py --story eol_saga --book book1 --subjects "chapters:000..004,characters:brenden"
  
  # Get everything flattened
  python bundle.py --story eol_saga --book book1 --subjects "*" --flat
  
  # Get all characters and places
  python bundle.py --story eol_saga --book book1 --subjects "characters:*,places:*"
  
  # Get specific character states
  python bundle.py --story eol_saga --book book1 --subjects "characters:brenden/farmboy,mireth/60s"
  
  # Specify custom output directory
  python bundle.py --story eol_saga --book book1 --subjects "characters:*/*" --output tools/bundle/bundles/all_characters
"""

from __future__ import annotations
import argparse
import json
from pathlib import Path
from typing import Any, List, Tuple, Dict
import re
import sys

# ------------------------------- utils ------------------------------------ #

def eprint(*args: Any) -> None:
    print(*args, file=sys.stderr)

def normalize_ext(ext: str | None) -> str:
    if not ext:
        return ""
    return ext if ext.startswith(".") else "." + ext

def natural_key(s: str):
    return [int(t) if t.isdigit() else t.lower() for t in re.findall(r"\d+|[^\d]+", s)]

# ---------------------------- range & glob -------------------------------- #

def expand_item_ranges(items: List[str]) -> List[str]:
    out: List[str] = []
    for it in items:
        if ".." not in it:
            out.append(it.strip())
            continue
        left, right = it.split("..", 1)
        def split_num(s: str):
            m = re.search(r"\d+", s)
            if not m:
                return (s, "", "")
            a, b = m.span()
            return (s[:a], s[a:b], s[b:])
        lp, ld, ls = split_num(left)
        rp, rd, rs = split_num(right)
        if not ld or not rd or lp != rp or ls != rs:
            out.append(it.strip())
            continue
        start, end = int(ld), int(rd)
        width = len(ld)
        step = 1 if end >= start else -1
        for n in range(start, end + step, step):
            out.append(f"{lp}{str(n).zfill(width)}{ls}")
    return out

def split_csv_patterns(s: str | None) -> List[str]:
    if not s:
        return []
    return [p.strip() for p in s.split(",") if p.strip()]

def parse_subject_configs(config_str: str) -> Dict[str, List[str]]:
    """
    Parse flexible subject:item configurations.
    
    Examples:
    - "chapters:000..004,characters:brenden" -> {"chapters": ["000..004"], "characters": ["brenden"]}
    - "*" -> {"*": ["*"]} (special case for getting everything)
    """
    if not config_str:
        return {}
    
    configs: Dict[str, List[str]] = {}
    
    # Handle special case for getting everything
    if config_str.strip() == "*":
        return {"*": ["*"]}
    
    for config in config_str.split(","):
        config = config.strip()
        if ":" in config:
            subject, items = config.split(":", 1)
            subject = subject.strip()
            items_list = split_csv_patterns(items)
            if subject and items_list:
                configs[subject] = items_list
        else:
            # If no colon, treat as subject with "*" items
            configs[config] = ["*"]
    
    return configs

# ------------------------------ resolver ---------------------------------- #

def resolve_character_patterns(
    characters_dir: Path,
    pattern: str,
    extension: str,
) -> List[Tuple[str, Path]]:
    """
    Resolve character patterns for the new nested directory structure.
    
    Supports patterns like:
    - "brenden" -> all files in brenden/ directory
    - "brenden/farmboy" -> specific character state
    - "*/farmboy" -> all farmboy states across characters
    - "brenden/*" -> all states for brenden
    - "*/*" -> all character states
    """
    selected: List[Tuple[str, Path]] = []
    
    # Handle patterns with slashes (character/state)
    if "/" in pattern:
        char_pattern, state_pattern = pattern.split("/", 1)
        
        # Find matching character directories
        char_dirs = list(characters_dir.glob(char_pattern))
        if not char_dirs:
            eprint(f"[warn] no character directories match: {char_pattern}")
            return []
        
        for char_dir in char_dirs:
            if not char_dir.is_dir():
                continue
            
            # Find matching state files
            if not Path(state_pattern).suffix:
                state_pattern = f"{state_pattern}{extension}"
            
            state_files = list(char_dir.glob(state_pattern))
            if not state_files:
                eprint(f"[warn] no state files match: {char_dir.name}/{state_pattern}")
                continue
            
            for state_file in state_files:
                if state_file.is_file():
                    label = f"characters/{char_dir.name}/{state_file.stem}"
                    selected.append((label, state_file.resolve()))
    
    else:
        # Single pattern - could be character name or state name
        # First try as character name
        char_dirs = list(characters_dir.glob(pattern))
        if char_dirs:
            for char_dir in char_dirs:
                if char_dir.is_dir():
                    # Get all files in this character directory
                    for state_file in char_dir.iterdir():
                        if state_file.is_file() and state_file.suffix == extension:
                            label = f"characters/{char_dir.name}/{state_file.stem}"
                            selected.append((label, state_file.resolve()))
        else:
            # Try as state name across all characters
            for char_dir in characters_dir.iterdir():
                if char_dir.is_dir():
                    if not Path(pattern).suffix:
                        pattern_with_ext = f"{pattern}{extension}"
                    else:
                        pattern_with_ext = pattern
                    
                    state_files = list(char_dir.glob(pattern_with_ext))
                    for state_file in state_files:
                        if state_file.is_file():
                            label = f"characters/{char_dir.name}/{state_file.stem}"
                            selected.append((label, state_file.resolve()))
    
    return selected

def resolve_place_patterns(
    places_dir: Path,
    pattern: str,
    extension: str,
) -> List[Tuple[str, Path]]:
    """
    Resolve place patterns for the nested directory structure.
    
    Supports patterns like:
    - "brannock_vale" -> all files in brannock_vale/ directory
    - "brannock_vale/brannock_vale" -> specific place file
    - "*/winter" -> all winter files across places
    - "brannock_vale/*" -> all files for brannock_vale
    - "*/*" -> all place files
    """
    selected: List[Tuple[str, Path]] = []
    
    # Handle patterns with slashes (place/file)
    if "/" in pattern:
        place_pattern, file_pattern = pattern.split("/", 1)
        
        # Find matching place directories
        place_dirs = list(places_dir.glob(place_pattern))
        if not place_dirs:
            eprint(f"[warn] no place directories match: {place_pattern}")
            return []
        
        for place_dir in place_dirs:
            if not place_dir.is_dir():
                continue
            
            # Find matching files
            if not Path(file_pattern).suffix:
                file_pattern = f"{file_pattern}{extension}"
            
            file_matches = list(place_dir.glob(file_pattern))
            if not file_matches:
                eprint(f"[warn] no files match: {place_dir.name}/{file_pattern}")
                continue
            
            for file_match in file_matches:
                if file_match.is_file():
                    label = f"places/{place_dir.name}/{file_match.stem}"
                    selected.append((label, file_match.resolve()))
    
    else:
        # Single pattern - could be place name or file name
        # First try as place name
        place_dirs = list(places_dir.glob(pattern))
        if place_dirs:
            for place_dir in place_dirs:
                if place_dir.is_dir():
                    # Get all files in this place directory
                    for file_match in place_dir.iterdir():
                        if file_match.is_file() and file_match.suffix == extension:
                            label = f"places/{place_dir.name}/{file_match.stem}"
                            selected.append((label, file_match.resolve()))
        else:
            # Try as file name across all places
            for place_dir in places_dir.iterdir():
                if place_dir.is_dir():
                    if not Path(pattern).suffix:
                        pattern_with_ext = f"{pattern}{extension}"
                    else:
                        pattern_with_ext = pattern
                    
                    file_matches = list(place_dir.glob(pattern_with_ext))
                    for file_match in file_matches:
                        if file_match.is_file():
                            label = f"places/{place_dir.name}/{file_match.stem}"
                            selected.append((label, file_match.resolve()))
    
    return selected

def resolve_subject(
    base_dir: Path,
    story: str,
    book: str,
    lang: str,
    subject: str,
    patterns_csv: str | None,
    extension: str,
) -> List[Tuple[str, Path]]:
    ext = normalize_ext(extension)
    subject_dir = (base_dir / story / book / lang / subject).resolve()
    items = split_csv_patterns(patterns_csv)
    if not items:
        return []
    items = expand_item_ranges(items)
    selected: List[Tuple[str, Path]] = []

    for item in items:
        # pattern inside subject_dir
        if not subject_dir.is_dir():
            eprint(f"[warn] subject dir not found: {subject_dir}")
            continue
        
        # Special handling for subjects with nested directory structure
        if subject in ["characters", "places"]:
            if subject == "characters":
                selected.extend(resolve_character_patterns(subject_dir, item, ext))
            elif subject == "places":
                selected.extend(resolve_place_patterns(subject_dir, item, ext))
        else:
            # Original behavior for other subjects
            pattern = item
            if not Path(pattern).suffix:
                # Special handling for chapters - they have "chapter-" prefix
                if subject == "chapters":
                    pattern = f"chapter-{pattern}{ext}"
                else:
                    pattern = f"{pattern}{ext}"
            matches = sorted(subject_dir.glob(pattern), key=lambda p: natural_key(p.name))
            if not matches:
                eprint(f"[warn] no matches: {story}/{book}/{lang}/{subject}/{item}")
                continue
            for p in matches:
                if p.is_file():
                    label = f"{subject}/{p.stem}"
                    selected.append((label, p.resolve()))

    # dedupe
    seen = set()
    out: List[Tuple[str, Path]] = []
    for label, p in selected:
        if str(p) not in seen:
            seen.add(str(p))
            out.append((label, p))
    return out

def discover_all_subjects(base_dir: Path, story: str, book: str, lang: str) -> Dict[str, List[str]]:
    """
    Discover all available subjects and their items.
    Returns a dict mapping subject names to lists of item patterns.
    """
    story_dir = base_dir / story / book / lang
    if not story_dir.is_dir():
        return {}
    
    subjects: Dict[str, List[str]] = {}
    
    for subject_dir in story_dir.iterdir():
        if not subject_dir.is_dir():
            continue
        
        subject_name = subject_dir.name
        items = []
        
        if subject_name == "characters":
            # Special handling for nested character structure
            for char_dir in subject_dir.iterdir():
                if char_dir.is_dir():
                    for state_file in char_dir.iterdir():
                        if state_file.is_file() and state_file.suffix == ".md":
                            items.append(f"{char_dir.name}/{state_file.stem}")
        elif subject_name == "places":
            # Special handling for nested place structure
            for place_dir in subject_dir.iterdir():
                if place_dir.is_dir():
                    for place_file in place_dir.iterdir():
                        if place_file.is_file() and place_file.suffix == ".md":
                            items.append(f"{place_dir.name}/{place_file.stem}")
        else:
            # Regular subject structure
            for item_file in subject_dir.iterdir():
                if item_file.is_file():
                    # Handle different extensions
                    if subject_name == "scaffolds" and item_file.suffix == ".md" and item_file.stem.endswith(".scaffold"):
                        # For scaffolds, use the base name without .scaffold suffix
                        stem = item_file.stem
                        items.append(stem[:-9])  # Remove ".scaffold" suffix
                    elif item_file.suffix == ".md":
                        if subject_name == "chapters":
                            # For chapters, remove the "chapter-" prefix to get the number
                            stem = item_file.stem
                            if stem.startswith("chapter-"):
                                items.append(stem[8:])  # Remove "chapter-" prefix
                            else:
                                items.append(stem)
                        else:
                            items.append(item_file.stem)
        
        if items:
            subjects[subject_name] = items
    
    return subjects

# ------------------------------- zipping ---------------------------------- #

def write_directory_and_manifest(files: List[Tuple[str, Path]], out_dir: Path, base_dir: Path, flat: bool = False) -> Dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)

    # manifest uses paths relative to repo root (base_dir)
    rel = lambda p: str(p.relative_to(base_dir))

    manifest = {
        "count": len(files),
        "files": [{"label": label, "path": rel(p)} for (label, p) in files],
    }

    # Copy files to directory
    for label, p in files:
        if flat:
            # Flattened structure: prefix with directory path
            # Convert label path to underscore-separated prefix
            path_prefix = label.replace("/", "_")
            dest_name = f"{path_prefix}{p.suffix}"
        else:
            # Keep subject/item structure
            dest_name = f"{label}{p.suffix}"
        
        dest_path = out_dir / dest_name
        # Create parent directories if needed (for non-flat mode)
        if not flat:
            dest_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Copy the file
        import shutil
        shutil.copy2(p, dest_path)
    
    # Write manifest to directory
    manifest_path = out_dir / "manifest.json"
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)

    return manifest

# --------------------------------- CLI ------------------------------------ #

def main(argv: List[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Bundle story files by subject into a directory; prints manifest to stdout.")
    ap.add_argument("--story", required=True, help="Story folder (e.g., eol-saga)")
    ap.add_argument("--book", required=True, help="Book folder (e.g., book1)")
    ap.add_argument("--lang", default="english", help="Language folder (default: english)")
    ap.add_argument("--subjects", required=True, help="Flexible subject:item configurations (e.g., 'chapters:000..004,characters:brenden' or '*' for everything)")
    ap.add_argument("--flat", action="store_true", help="Flatten output structure (default: false)")
    ap.add_argument("--extension", default=".md", help="Default extension (default: .md)")
    ap.add_argument("--output", default="tools/bundle/bundles/story_bundle", help="Output directory path (default: tools/bundle/bundles/story_bundle)")
    ap.add_argument("--base-dir", default=".", help="Repo root (default: .)")
    args = ap.parse_args(argv)

    base_dir = Path(args.base_dir).resolve()
    subject_configs = parse_subject_configs(args.subjects)

    all_files: List[Tuple[str, Path]] = []
    
    # Handle special case for getting everything
    if "*" in subject_configs and subject_configs["*"] == ["*"]:
        all_subjects = discover_all_subjects(base_dir, args.story, args.book, args.lang)
        for subject, items in all_subjects.items():
            for item in items:
                if subject == "characters" and "/" in item:
                    # Character state
                    char_name, state_name = item.split("/", 1)
                    files = resolve_subject(base_dir, args.story, args.book, args.lang, subject, f"{char_name}/{state_name}", args.extension)
                elif subject == "places" and "/" in item:
                    # Place file
                    place_name, file_name = item.split("/", 1)
                    files = resolve_subject(base_dir, args.story, args.book, args.lang, subject, f"{place_name}/{file_name}", args.extension)
                elif subject == "scaffolds":
                    # Scaffolds use .scaffold.md extension
                    files = resolve_subject(base_dir, args.story, args.book, args.lang, subject, item, ".scaffold.md")
                else:
                    # Regular item
                    files = resolve_subject(base_dir, args.story, args.book, args.lang, subject, item, args.extension)
                all_files.extend(files)
    else:
        # Handle specific subject configurations
        for subject, items in subject_configs.items():
            for item in items:
                if subject == "characters":
                    # For characters, we need to handle the nested structure properly
                    files = resolve_subject(base_dir, args.story, args.book, args.lang, subject, item, args.extension)
                elif subject == "places":
                    # For places, we need to handle the nested structure properly
                    files = resolve_subject(base_dir, args.story, args.book, args.lang, subject, item, args.extension)
                elif subject == "scaffolds":
                    # Scaffolds use .scaffold.md extension
                    files = resolve_subject(base_dir, args.story, args.book, args.lang, subject, item, ".scaffold.md")
                else:
                    files = resolve_subject(base_dir, args.story, args.book, args.lang, subject, item, args.extension)
                all_files.extend(files)

    if not all_files:
        eprint("[info] No files matched any patterns.")
        print(json.dumps({"count": 0, "files": []}, indent=2))
        return 0

    all_files.sort(key=lambda t: (t[0].split("/")[0], natural_key(t[0]), natural_key(t[1].name)))

    manifest = write_directory_and_manifest(all_files, Path(args.output), base_dir, args.flat)
    print(json.dumps(manifest, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
