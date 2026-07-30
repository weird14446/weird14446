#!/usr/bin/env python3
import os
import re
from pathlib import Path
import urllib.parse

def format_title_from_filename(filename: str) -> str:
    """Creates a readable paper title from a PDF filename."""
    name_without_ext = Path(filename).stem
    # Replace underscores and hyphens with spaces if they separate words
    cleaned_name = name_without_ext.replace("_", " ").replace("-", " ")
    # Collapse multiple spaces
    cleaned_name = re.sub(r"\s+", " ", cleaned_name).strip()
    return cleaned_name

def get_paper_title(pdf_path: Path) -> str:
    """Attempts to extract PDF title metadata, falls back to formatted filename."""
    # Try pypdf if installed
    try:
        import pypdf
        reader = pypdf.PdfReader(pdf_path)
        if reader.metadata and reader.metadata.title:
            title = reader.metadata.title.strip()
            if len(title) > 3 and not title.lower().endswith(".pdf"):
                return title
    except Exception:
        pass
    
    return format_title_from_filename(pdf_path.name)

def generate_papers_markdown(papers_dir: Path) -> str:
    """Scans the papers directory and returns formatted markdown."""
    pdf_files = sorted(
        [f for f in papers_dir.glob("*.pdf") if f.is_file()],
        key=lambda x: x.name.lower()
    )

    if not pdf_files:
        return "*No papers uploaded yet.*"

    lines = []
    lines.append("| Paper Title | Link |")
    lines.append("| :--- | :---: |")

    for pdf in pdf_files:
        title = get_paper_title(pdf)
        encoded_path = f"./papers/{urllib.parse.quote(pdf.name)}"
        lines.append(f"| **{title}** | [📄 Download PDF]({encoded_path}) |")

    return "\n".join(lines)

def update_readme(readme_path: Path, new_content: str):
    """Replaces content between PAPERS_LIST_START and PAPERS_LIST_END in README.md."""
    if not readme_path.exists():
        print(f"Error: {readme_path} not found.")
        return

    with open(readme_path, "r", encoding="utf-8") as f:
        content = f.read()

    pattern = r"(<!-- PAPERS_LIST_START -->)(.*?)(<!-- PAPERS_LIST_END -->)"
    replacement = f"\\1\n{new_content}\n\\3"

    new_readme, count = re.subn(pattern, replacement, content, flags=re.DOTALL)

    if count == 0:
        print("Warning: Could not find PAPERS_LIST_START and PAPERS_LIST_END markers in README.md")
        return

    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(new_readme)

    print(f"Successfully updated {readme_path} with {count} section(s) replaced.")

def main():
    repo_root = Path(__file__).resolve().parent.parent
    papers_dir = repo_root / "papers"
    readme_path = repo_root / "README.md"

    if not papers_dir.exists():
        papers_dir.mkdir(parents=True, exist_ok=True)

    markdown_papers = generate_papers_markdown(papers_dir)
    update_readme(readme_path, markdown_papers)

if __name__ == "__main__":
    main()
