"""Main module."""
import sys
import unicodedata
from bs4 import BeautifulSoup
from highlights_prettifier.fix_titles import fix_titles
from highlights_prettifier.format_highlights import create_formated_highlights
from highlights_prettifier.parse_highlights import get_highlights_from_raw_text
from pathlib import Path
import pypandoc

from ebooklib import epub


def save_to_file(markdown, output_file):
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(markdown)


FILES_DIR = "data/PragmaticProgrammer"


if __name__ == "__main__":
    article_epub_file_path = FILES_DIR + "/article.epub"
    article_html_file_path = FILES_DIR + "/article.html"
    article_md_file_path = FILES_DIR + "/article.md"
    output_html_file = FILES_DIR + "/output.html"
    highlights_file = FILES_DIR + "/highlights.md"
    output_md_file = FILES_DIR + "/output.md"
    # Read input from the input.md file
    input_text = ""
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

    with open(article_html_file_path) as fp:
        soup = BeautifulSoup(fp, "html.parser")
    if not soup:
        print(
            "Article file doesn't exist at provided path "
            f"{article_html_file_path}"
        )
        sys.exit()

    # TODO: Extract and infer titles from table of contents
    book = epub.read_epub(article_epub_file_path)
    fixed_soup = fix_titles(book, soup)
    # TODO: Save soup to file

    # Convert html to MD
    if not Path(article_md_file_path).exists():
        if Path(article_html_file_path).exists():
            output = pypandoc.convert_file(
                source_file=article_html_file_path,
                format="html",
                outputfile=article_md_file_path,
                to="gfm",
            )
        else:
            print(
                "Article file doesn't exist at provided path "
                f"{article_html_file_path}"
            )
            sys.exit()

    # Open pre-processed files
    with open(highlights_file, "r", encoding="utf-8") as file:
        input_text = file.read()
        normalized_highlights_text = unicodedata.normalize(
            "NFKD", input_text
        ).replace("\u200b", "")
    with open(article_md_file_path, "r", encoding="utf-8") as file:
        article_text = file.read()
        # TODO Use only one unicode library
        normalized_article_text = unicodedata.normalize(
            "NFKD", article_text
        ).replace("\u200b", "")

    highlights = get_highlights_from_raw_text(normalized_highlights_text)
    formatted_highlights_html = create_formated_highlights(
        normalized_article_text, highlights
    )
    save_to_file(formatted_highlights_html, output_html_file)
    formatted_highlights_md = pypandoc.convert_text(
        source=formatted_highlights_html,
        format="html",
        to="gfm",
    )
    save_to_file(formatted_highlights_md, output_md_file)

    print(f"Formatted highlights saved to {output_md_file}")
