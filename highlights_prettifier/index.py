"""Main module."""
from format_highlights import create_formated_highlights
from parse_highlights import get_highlights_from_raw_text


def save_markdown_to_file(markdown, output_file):
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(markdown)


if __name__ == "__main__":
    article_file_path = "article_sample.md"
    output_file = "data/output.md"
    input_file = "highlights_sample.md"
    # Read input from the input.md file
    input_text = ""
    article_text = ""
    with open(input_file, "r", encoding="utf-8") as file:
        input_text = file.read()
    with open(article_file_path, "r", encoding="utf-8") as file:
        article_text = file.read()

    highlights = get_highlights_from_raw_text(input_text)
    formatted_highlights = create_formated_highlights(article_text, highlights)
    save_markdown_to_file(formatted_highlights, output_file)

    print(f"Formatted highlights saved to {output_file}")