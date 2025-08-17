# EPUB Builder Tool

This tool packages book versions into EPUB format for easy reading on e-readers and mobile devices.

## Features

- Converts markdown chapters to EPUB format
- Supports multiple stories/sagas (eol-saga, wonderlight-saga, etc.)
- Configurable chapter ranges
- Automatic table of contents generation
- Proper EPUB metadata and structure

## Usage

```bash
cd tools/epub
python3 epub_builder.py <story> <book> <language> <to-chapter> [output-dir]
```

### Parameters

- **story**: The story/saga name (e.g., 'eol-saga', 'wonderlight-saga')
- **book**: The book number (e.g., 'book1', 'book2')
- **language**: The language version (e.g., 'english', 'spanish')
- **to-chapter**: The last chapter to include (e.g., 'chapter-004', 'chapter-002')
- **output-dir**: Output directory for EPUB files (optional, defaults to current directory)

### Examples

```bash
# Create EPUB with all chapters up to chapter-004 (in current directory)
python3 epub_builder.py eol-saga book1 english chapter-004

# Create EPUB with chapters up to chapter-002 only (in current directory)
python3 epub_builder.py eol-saga book1 english chapter-002

# Create EPUB for wonderlight-saga (in current directory)
python3 epub_builder.py wonderlight-saga book1 english chapter-001

# Create EPUB in a specific output directory
python3 epub_builder.py eol-saga book1 english chapter-004 /path/to/output

# Create EPUB in a relative output directory
python3 epub_builder.py eol-saga book1 english chapter-003 ../output
```

## Output

The script creates EPUB files named according to the pattern:
`{story}-{book}-{language}.epub`

For example:
- `eol-saga-book1-english.epub`
- `wonderlight-saga-book1-english.epub`

## File Structure

The script expects the following directory structure:
```
{story}/
  {book}/
    {language}/
      chapters/
        chapter-000.md
        chapter-001.md
        chapter-002.md
        ...
```

## EPUB Features

- **Table of Contents**: Automatically generated from chapter titles
- **Metadata**: Includes title, language, creation date, and unique identifier
- **Chapter Navigation**: Each chapter is a separate XHTML file
- **Markdown Conversion**: Converts markdown formatting to HTML
  - Headers (# ## ###)
  - Bold (**text**)
  - Italic (*text*)
  - Paragraphs

## Requirements

- Python 3.6+
- Standard library modules (no external dependencies)

## Notes

- The script only includes text chapters (markdown files)
- Character files, guidelines, and other assets are not included
- Chapters are included in alphabetical order up to the specified `to-chapter`
- The EPUB follows the EPUB 3.0 specification
