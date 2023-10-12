"""Main module."""
import unicodedata
from format_highlights import create_formated_highlights
from parse_highlights import get_highlights_from_raw_text


def save_markdown_to_file(markdown, output_file):
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(markdown)


if __name__ == "__main__":
    article_file_path = "data/markdown_ebook.md"
    output_file = "data/output.html"  # Then transform to MD with pandoc
    input_file = "data/input.md"
    # Read input from the input.md file
    input_text = ""
    article_text = ""
    with open(input_file, "r", encoding="utf-8") as file:
        input_text = file.read()
        normalized_highlights_text = unicodedata.normalize("NFKD", input_text).replace(
            "\u200b", ""
        )
    with open(article_file_path, "r", encoding="utf-8") as file:
        article_text = file.read()
        normalized_article_text = unicodedata.normalize("NFKD", article_text).replace(
            "\u200b", ""
        )

    highlights = get_highlights_from_raw_text(normalized_highlights_text)
    formatted_highlights = create_formated_highlights(
        normalized_article_text, highlights
    )
    save_markdown_to_file(formatted_highlights, output_file)

    print(f"Formatted highlights saved to {output_file}")
