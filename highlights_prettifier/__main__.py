"""Main module."""
import sys
import unicodedata
from pathlib import Path

import pypandoc
from bs4 import BeautifulSoup
from ebooklib import epub

from highlights_prettifier.fix_titles import fix_titles
from highlights_prettifier.format_highlights import create_formated_highlights
from highlights_prettifier.parse_highlights import get_highlights_from_raw_text


def save_to_file(text, output_file):
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(text)


def read_from_file(file):
    with open(file, "r") as f:
        return f.read()


FILES_DIR = "data/PragmaticProgrammer"
DEBUG = True

if __name__ == "__main__":
    article_epub_file_path = FILES_DIR + "/article.epub"
    article_html_file_path = FILES_DIR + "/article.html"
    article_fixed_html_file_path = FILES_DIR + "/article_fixed.html"
    article_md_file_path = FILES_DIR + "/article.md"
    article_md_normalized_file_path = FILES_DIR + "/article_normalized.md"
    output_html_file = FILES_DIR + "/output.html"
    highlights_file = FILES_DIR + "/highlights.md"
    output_md_file = FILES_DIR + "/output.md"
    # Read input from the input.md file
    input_text = ""
    article_text = ""
    article_text = ""

    # Convert epub to html
    if not Path(article_html_file_path).exists():
        if Path(article_epub_file_path).exists():
            output = pypandoc.convert_file(
                source_file=article_epub_file_path,
                format="epub",
                outputfile=article_html_file_path,
                to="html",
            )
        else:
            print(
                "Article file doesn't exist at provided path "
                f"{article_epub_file_path}"
            )
            sys.exit()

    article_text_html = read_from_file(article_html_file_path)
    soup = BeautifulSoup(article_text_html, "html.parser")

    # TODO: Extract and infer titles from table of contents
    book = epub.read_epub(article_epub_file_path)
    fixed_soup = fix_titles(book, soup)

    if DEBUG:
        save_to_file(
            text=str(fixed_soup), output_file=article_fixed_html_file_path
        )

    article_text_gfm = pypandoc.convert_text(
        source=fixed_soup, format="html", to="gfm"
    )

    if DEBUG:
        save_to_file(text=str(fixed_soup), output_file=article_md_file_path)

    # Open pre-processed files
    with open(highlights_file, "r", encoding="utf-8") as file:
        input_text = file.read()
        normalized_highlights_text = unicodedata.normalize(
            "NFKD", input_text
        ).replace("\u200b", "")

    # TODO Use only one unicode library
    normalized_article_text = unicodedata.normalize(
        "NFKD", article_text_gfm
    ).replace("\u200b", "")
    if DEBUG:
        save_to_file(
            text=normalized_article_text,
            output_file=article_md_normalized_file_path,
        )

    highlights = get_highlights_from_raw_text(normalized_highlights_text)
    formatted_highlights_html = create_formated_highlights(
        normalized_article_text, highlights
    )
    if DEBUG:
        save_to_file(formatted_highlights_html, output_html_file)
    formatted_highlights_md = pypandoc.convert_text(
        source=formatted_highlights_html,
        format="html",
        to="gfm",
    )
    save_to_file(formatted_highlights_md, output_md_file)

    print(f"Formatted highlights saved to {output_md_file}")
