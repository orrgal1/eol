#!/usr/bin/env python3
"""
EPUB Builder for Book Packaging

This script packages a book version into EPUB format with the following parameters:
- story: The story/saga name (e.g., 'eol-saga', 'wonderlight-saga')
- book: The book number (e.g., 'book1')
- language: The language version (e.g., 'english')
- to-chapter: The last chapter to include (e.g., 'chapter-004')
- output-dir: Output directory for EPUB files (optional, defaults to current directory)

Usage:
    python epub_builder.py <story> <book> <language> <to-chapter> [output-dir]
    
Example:
    python epub_builder.py eol-saga book1 english chapter-004
    python epub_builder.py eol-saga book1 english chapter-004 /path/to/output
"""

import os
import sys
import zipfile
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
import re

class EPUBBuilder:
    def __init__(self, story, book, language, to_chapter, output_dir=None):
        self.story = story
        self.book = book
        self.language = language
        self.to_chapter = to_chapter
        self.output_dir = Path(output_dir) if output_dir else Path.cwd()
        self.workspace_root = Path(__file__).parent.parent.parent
        self.book_path = self.workspace_root / story / book / language
        # Try chapters subdirectory first, then fall back to language directory
        self.chapters_path = self.book_path / "chapters"
        if not self.chapters_path.exists():
            self.chapters_path = self.book_path
        
    def validate_paths(self):
        """Validate that all required paths exist."""
        if not self.book_path.exists():
            raise FileNotFoundError(f"Book path not found: {self.book_path}")
        
        # Create output directory if it doesn't exist
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        return True
    
    def get_chapter_files(self):
        """Get all chapter files up to the specified to-chapter."""
        if not self.chapters_path.exists():
            return []
        
        chapter_files = []
        for file in sorted(self.chapters_path.glob("chapter-*.md")):
            chapter_files.append(file)
            if file.name == f"{self.to_chapter}.md":
                break
        
        return chapter_files
    
    def extract_title_from_chapter(self, chapter_content):
        """Extract the title from chapter content (first # heading)."""
        lines = chapter_content.split('\n')
        for line in lines:
            if line.strip().startswith('# '):
                return line.strip()[2:].strip()
        return "Untitled Chapter"
    
    def create_cover_page(self):
        """Create a cover page with the book title."""
        book_title = f"{self.story.title()} - {self.book.title()}"
        subtitle = f"{self.language.title()} Edition"
        
        cover_html = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
    <title>Cover</title>
    <meta charset="utf-8"/>
    <style>
        body {{
            margin: 0;
            padding: 0;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            font-family: "Times New Roman", serif;
            color: #ffffff;
            height: 100vh;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            text-align: center;
        }}
        .cover-container {{
            max-width: 80%;
            padding: 2em;
        }}
        .title {{
            font-size: 2.5em;
            font-weight: bold;
            margin-bottom: 0.5em;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
            line-height: 1.2;
        }}
        .subtitle {{
            font-size: 1.2em;
            margin-bottom: 2em;
            opacity: 0.9;
            font-style: italic;
        }}
        .author {{
            font-size: 1.1em;
            margin-top: 2em;
            opacity: 0.8;
        }}
        .decoration {{
            font-size: 3em;
            margin: 1em 0;
            opacity: 0.6;
        }}
    </style>
</head>
<body>
    <div class="cover-container">
        <div class="decoration">✦</div>
        <h1 class="title">{book_title}</h1>
        <div class="subtitle">{subtitle}</div>
        <div class="decoration">✦</div>
        <div class="author">A Tale of Light and Darkness</div>
    </div>
</body>
</html>'''
        
        return cover_html
    
    def markdown_to_html(self, markdown_content):
        """Convert markdown content to HTML."""
        # Simple markdown to HTML conversion
        html = markdown_content
        
        # Convert headers
        html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
        html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
        html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
        
        # Convert paragraphs
        html = re.sub(r'^([^<].+)$', r'<p>\1</p>', html, flags=re.MULTILINE)
        
        # Remove empty paragraphs
        html = re.sub(r'<p></p>', '', html)
        
        # Convert emphasis
        html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
        html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)
        
        # Convert line breaks
        html = html.replace('\n\n', '</p>\n<p>')
        
        return html
    
    def create_epub_structure(self, chapter_files):
        """Create the EPUB file structure."""
        epub_filename = f"{self.story}-{self.book}-{self.language}.epub"
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create META-INF directory
            meta_inf = temp_path / "META-INF"
            meta_inf.mkdir()
            
            # Create container.xml
            container_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
    <rootfiles>
        <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
    </rootfiles>
</container>'''
            
            with open(meta_inf / "container.xml", 'w', encoding='utf-8') as f:
                f.write(container_xml)
            
            # Create OEBPS directory
            oebps = temp_path / "OEBPS"
            oebps.mkdir()
            
            # Create cover page
            cover_html = self.create_cover_page()
            with open(oebps / "cover.xhtml", 'w', encoding='utf-8') as f:
                f.write(cover_html)
            
            # Create content.opf
            content_opf = self.create_content_opf(chapter_files)
            with open(oebps / "content.opf", 'w', encoding='utf-8') as f:
                f.write(content_opf)
            
            # Create toc.ncx
            toc_ncx = self.create_toc_ncx(chapter_files)
            with open(oebps / "toc.ncx", 'w', encoding='utf-8') as f:
                f.write(toc_ncx)
            
            # Create chapter HTML files
            for i, chapter_file in enumerate(chapter_files):
                with open(chapter_file, 'r', encoding='utf-8') as f:
                    chapter_content = f.read()
                
                chapter_title = self.extract_title_from_chapter(chapter_content)
                chapter_html = self.markdown_to_html(chapter_content)
                
                html_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
    <title>{chapter_title}</title>
    <meta charset="utf-8"/>
</head>
<body>
    {chapter_html}
</body>
</html>'''
                
                with open(oebps / f"chapter_{i:03d}.xhtml", 'w', encoding='utf-8') as f:
                    f.write(html_content)
            
            # Create mimetype file
            with open(temp_path / "mimetype", 'w', encoding='utf-8') as f:
                f.write("application/epub+zip")
            
            # Create EPUB file
            epub_path = self.output_dir / epub_filename
            
            with zipfile.ZipFile(epub_path, 'w', zipfile.ZIP_DEFLATED) as epub_zip:
                # Add mimetype first (EPUB requirement)
                epub_zip.write(temp_path / "mimetype", "mimetype")
                
                # Add all other files
                for file_path in temp_path.rglob("*"):
                    if file_path.is_file() and file_path.name != "mimetype":
                        relative_path = file_path.relative_to(temp_path)
                        epub_zip.write(file_path, relative_path)
            
            print(f"EPUB created successfully: {epub_path}")
            return epub_path
    
    def create_content_opf(self, chapter_files):
        """Create the content.opf file."""
        book_title = f"{self.story.title()} - {self.book.title()} - {self.language.title()}"
        
        manifest_items = []
        spine_items = []
        
        # Add navigation
        manifest_items.append('    <item id="toc" href="toc.ncx" media-type="application/x-dtbncx+xml"/>')
        
        # Add cover page
        manifest_items.append('    <item id="cover" href="cover.xhtml" media-type="application/xhtml+xml"/>')
        spine_items.append('    <itemref idref="cover"/>')
        
        # Add chapters
        for i, chapter_file in enumerate(chapter_files):
            chapter_title = self.extract_title_from_chapter(chapter_file.read_text(encoding='utf-8'))
            manifest_items.append(f'    <item id="chapter_{i:03d}" href="chapter_{i:03d}.xhtml" media-type="application/xhtml+xml"/>')
            spine_items.append(f'    <itemref idref="chapter_{i:03d}"/>')
        
        manifest_content = '\n'.join(manifest_items)
        spine_content = '\n'.join(spine_items)
        
        content_opf = f'''<?xml version="1.0" encoding="UTF-8"?>
<package version="3.0" xmlns="http://www.idpf.org/2007/opf">
    <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
        <dc:title>{book_title}</dc:title>
        <dc:creator>Author</dc:creator>
        <dc:language>{self.language}</dc:language>
        <dc:identifier id="bookid">urn:uuid:{self.story}-{self.book}-{self.language}</dc:identifier>
        <dc:date>{datetime.now().strftime('%Y-%m-%d')}</dc:date>
    </metadata>
    <manifest>
{manifest_content}
    </manifest>
    <spine toc="toc">
{spine_content}
    </spine>
</package>'''
        
        return content_opf
    
    def create_toc_ncx(self, chapter_files):
        """Create the toc.ncx file."""
        book_title = f"{self.story.title()} - {self.book.title()} - {self.language.title()}"
        
        nav_points = []
        
        # Add cover page
        nav_points.append(f'''        <navPoint id="cover" playOrder="1">
            <navLabel>
                <text>Cover</text>
            </navLabel>
            <content src="cover.xhtml"/>
        </navPoint>''')
        
        # Add chapters
        for i, chapter_file in enumerate(chapter_files):
            chapter_title = self.extract_title_from_chapter(chapter_file.read_text(encoding='utf-8'))
            nav_points.append(f'''        <navPoint id="chapter_{i:03d}" playOrder="{i+2}">
            <navLabel>
                <text>{chapter_title}</text>
            </navLabel>
            <content src="chapter_{i:03d}.xhtml"/>
        </navPoint>''')
        
        nav_content = '\n'.join(nav_points)
        
        toc_ncx = f'''<?xml version="1.0" encoding="UTF-8"?>
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">
    <head>
        <meta name="dtb:uid" content="urn:uuid:{self.story}-{self.book}-{self.language}"/>
        <meta name="dtb:depth" content="1"/>
        <meta name="dtb:totalPageCount" content="0"/>
        <meta name="dtb:maxPageNumber" content="0"/>
    </head>
    <docTitle>
        <text>{book_title}</text>
    </docTitle>
    <navMap>
{nav_content}
    </navMap>
</ncx>'''
        
        return toc_ncx
    
    def build(self):
        """Build the EPUB file."""
        try:
            self.validate_paths()
            chapter_files = self.get_chapter_files()
            
            if not chapter_files:
                print(f"No chapter files found in {self.chapters_path}")
                return None
            
            print(f"Found {len(chapter_files)} chapters:")
            for chapter_file in chapter_files:
                print(f"  - {chapter_file.name}")
            
            epub_path = self.create_epub_structure(chapter_files)
            return epub_path
            
        except Exception as e:
            print(f"Error building EPUB: {e}")
            return None

def main():
    if len(sys.argv) < 5 or len(sys.argv) > 6:
        print(__doc__)
        sys.exit(1)
    
    story = sys.argv[1]
    book = sys.argv[2]
    language = sys.argv[3]
    to_chapter = sys.argv[4]
    output_dir = sys.argv[5] if len(sys.argv) == 6 else None
    
    builder = EPUBBuilder(story, book, language, to_chapter, output_dir)
    result = builder.build()
    
    if result:
        print(f"\nEPUB successfully created: {result}")
    else:
        print("\nFailed to create EPUB")
        sys.exit(1)

if __name__ == "__main__":
    main()
