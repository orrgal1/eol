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
- Outputs a ZIP and prints a manifest (paths relative to --base-dir)

Flags:
  --story       Story folder (e.g., eol_saga)
  --book        Book folder (e.g., book1)
  --lang        Language folder (default: english)
  --chapters    Comma-separated patterns (ranges/globs/paths)
  --characters  Comma-separated patterns (character names, states, or character/state)
  --guidelines  Comma-separated patterns (ranges/globs/paths)
  --artifacts   Comma-separated patterns (ranges/globs/paths)
  --places      Comma-separated patterns (ranges/globs/paths)
  --extension   Default extension to append (default: .md)
  --bundle      Output ZIP path (default: tools/bundle/bundles/story_bundle.zip)
  --base-dir    Repo root (default: current directory)

Example:
  python bundle.py \
    --story eol_saga \
    --book book1 \
    --lang english \
    --chapters 000..004 \
    --characters brenden,brenden/farmboy,mireth/60s,*/* \
    --guidelines writing \
    --artifacts twin_blades \
    --places brannock_vale \
    --bundle tools/bundle/bundles/chapter5_context.zip
"""

from __future__ import annotations
import argparse
import json
from pathlib import Path
from typing import Any, List, Tuple, Dict
import re
import sys
import zipfile

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
        
        # Special handling for characters with nested directory structure
        if subject == "characters":
            selected.extend(resolve_character_patterns(subject_dir, item, ext))
        else:
            # Original behavior for other subjects
            pattern = item
            if not Path(pattern).suffix:
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

# ------------------------------- zipping ---------------------------------- #

def write_zip_and_manifest(files: List[Tuple[str, Path]], out_zip: Path, base_dir: Path) -> Dict[str, Any]:
    out_zip.parent.mkdir(parents=True, exist_ok=True)

    # manifest uses paths relative to repo root (base_dir)
    rel = lambda p: str(p.relative_to(base_dir))

    manifest = {
        "count": len(files),
        "files": [{"label": label, "path": rel(p)} for (label, p) in files],
    }

    # ZIP
    with zipfile.ZipFile(out_zip, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for label, p in files:
            arcname = f"{label}{p.suffix}"  # keep subject/item structure in archive
            zf.write(p, arcname=arcname)
        # Embed manifest inside the zip as well
        zf.writestr("manifest.json", json.dumps(manifest, indent=2))

    return manifest

# --------------------------------- CLI ------------------------------------ #

def main(argv: List[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Bundle story files by subject into a ZIP; prints manifest to stdout.")
    ap.add_argument("--story", required=True, help="Story folder (e.g., eol-saga)")
    ap.add_argument("--book", required=True, help="Book folder (e.g., book1)")
    ap.add_argument("--lang", default="english", help="Language folder (default: english)")
    ap.add_argument("--chapters", help="Comma-separated patterns")
    ap.add_argument("--characters", help="Comma-separated patterns")
    ap.add_argument("--guidelines", help="Comma-separated patterns")
    ap.add_argument("--artifacts", help="Comma-separated patterns")
    ap.add_argument("--places", help="Comma-separated patterns")
    ap.add_argument("--extension", default=".md", help="Default extension (default: .md)")
    ap.add_argument("--bundle", default="tools/bundle/bundles/story_bundle.zip", help="Output ZIP path (default: tools/bundle/bundles/story_bundle.zip)")
    ap.add_argument("--base-dir", default=".", help="Repo root (default: .)")
    args = ap.parse_args(argv)

    base_dir = Path(args.base_dir).resolve()
    subjects: Dict[str, str | None] = {
        "chapters": args.chapters,
        "characters": args.characters,
        "guidelines": args.guidelines,
        "artifacts": args.artifacts,
        "places": args.places,
    }

    all_files: List[Tuple[str, Path]] = []
    for subject, patterns in subjects.items():
        if not patterns:
            continue
        files = resolve_subject(base_dir, args.story, args.book, args.lang, subject, patterns, args.extension)
        all_files.extend(files)

    if not all_files:
        eprint("[info] No files matched any patterns.")
        print(json.dumps({"count": 0, "files": []}, indent=2))
        return 0

    all_files.sort(key=lambda t: (t[0].split("/")[0], natural_key(t[0]), natural_key(t[1].name)))

    manifest = write_zip_and_manifest(all_files, Path(args.bundle), base_dir)
    print(json.dumps(manifest, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
