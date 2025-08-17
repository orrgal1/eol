# GitHub Actions Workflows

This directory contains GitHub Actions workflows that automate various tasks for the repository.

## Workflows

### Build EPUBs (`build-epubs.yml`)

**Trigger**: Push to `main` branch with changes to chapter files (after PR merge)

**What it does**:
- Detects which books have had chapter files modified
- Automatically builds EPUB files for those books
- Includes all chapters up to the highest available chapter number
- Generates EPUBs with cover pages and proper metadata

**Trigger conditions**:
- Changes to files matching `**/chapters/**/*.md`
- Changes to files matching `**/book*/**/*.md`

**Output**:
- EPUB files are generated in `{story}/{book}/epubs/` directories
- Files are named `{story}-{book}-{language}.epub`
- A pull request is automatically created with the EPUB changes
- A summary is provided in the PR description

**Example**:
When you merge a PR with changes to `eol-saga/book1/english/chapters/chapter-005.md` to main, the workflow will:
1. Detect that `eol-saga/book1/english` has changes
2. Find the highest chapter number (005)
3. Build `eol-saga/book1/epubs/eol-saga-book1-english.epub`
4. Include chapters 000-005 with a cover page
5. Create a pull request with the EPUB changes

**Automatic Pull Request**:
The workflow automatically creates a pull request with the generated EPUB files. This allows for review before merging the EPUBs to the main branch.

### CLA Check (`cla-check.yml`)

**Trigger**: Pull requests

**What it does**:
- Checks if contributors have signed the Contributor License Agreement
- Ensures compliance with the project's licensing requirements

## Usage

These workflows run automatically when the trigger conditions are met. No manual intervention is required for the build process.

To view workflow runs:
1. Go to the "Actions" tab on GitHub
2. Select the workflow you want to view
3. Check the logs and outputs

## Troubleshooting

### EPUB Build Failures
- Check that chapter files follow the naming convention `chapter-XXX.md`
- Ensure the book structure matches: `{story}/{book}/{language}/chapters/`
- Verify that Python 3.11+ is available (handled automatically by the workflow)

### Missing EPUBs
- The workflow only builds EPUBs for books that have had chapter changes
- Check the workflow logs to see which books were detected as changed
- Ensure chapter files are in the correct directory structure
