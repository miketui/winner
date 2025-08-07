import re
from pathlib import Path
import frontmatter
from markdown import Markdown
from jinja2 import Environment, FileSystemLoader

TEMPLATE_DIR = Path("templates")
OUTPUT_DIR = Path("xhtml")
OUTPUT_DIR.mkdir(exist_ok=True)

env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)))
template = env.get_template("chapter.xhtml.j2")


def split_section(src: str, marker: str):
    pattern = rf"\n## {marker}\n"
    parts = re.split(pattern, src, maxsplit=1)
    if len(parts) == 2:
        return parts[0], parts[1]
    return src, ""


for md_path in sorted(Path(".").glob("*-Chapter-*_final.md")):
    post = frontmatter.load(md_path)
    text = post.content

    body, rest = split_section(text, "Quiz")
    quiz, rest = split_section(rest, "Worksheet")
    worksheet, rest = split_section(rest, "Image Quote")
    closing, endnotes = split_section(rest, "Endnotes")

    md = Markdown(extensions=["extra", "tables", "fenced_code", "footnotes"])
    content_html = md.convert(body)
    md = Markdown(extensions=["extra", "tables", "fenced_code", "footnotes"])
    quiz_html = md.convert(quiz)
    md = Markdown(extensions=["extra", "tables", "fenced_code", "footnotes"])
    worksheet_html = md.convert(worksheet)
    md = Markdown(extensions=["extra", "tables", "fenced_code", "footnotes"])
    endnotes_html = md.convert(endnotes)
    content_html += endnotes_html

    match = re.search(r"!\[(?P<alt>[^\]]*)\]\((?P<src>[^)]+)\)", closing)
    if match:
        image_src = Path(match.group("src")).name
        image_alt = match.group("alt")
    else:
        image_src = ""
        image_alt = ""

    title_full = post.get("title", md_path.stem)
    roman = post.get("chapter_number", "")
    title_part = title_full.split(":", 1)[-1].strip().upper()
    title_lines = title_part.split()

    html = template.render(
        title_full=title_full,
        roman_numeral=roman,
        title_lines=title_lines,
        content_html=content_html,
        quiz_html=quiz_html,
        worksheet_html=worksheet_html,
        closing_image=image_src,
        closing_alt=image_alt,
    )

    output_name = md_path.stem.replace("_final", "") + ".xhtml"
    output_path = OUTPUT_DIR / output_name
    output_path.write_text(html, encoding="utf-8")
    print(f"Wrote {output_path}")
