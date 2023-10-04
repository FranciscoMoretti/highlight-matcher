"""Main module."""
import re
import nltk

from syntax_tree import filter_syntax_tree, walk_up_find
from mdformat.renderer import MDRenderer
from markdown_it import MarkdownIt
from rapidfuzz import fuzz, process
from markdown_it.tree import SyntaxTreeNode

nltk.download("punkt")

# Customize the fuzziness threshold
FUZZY_MATCH_MIN_SCORE = 90  # Adjust as needed


def extract_highlights_from_md(article_text, highlights):
    mdit = MarkdownIt()
    env = {}
    tokens = mdit.parse(article_text, env)

    syntax_tree = SyntaxTreeNode(tokens)
    # Create a dummy root node to hold the filtered nodes

    # Define a simple evaluation function to keep heading nodes
    def partially_matches_highlight_or_heading(node: SyntaxTreeNode):
        if node.children:
            return True
        elif walk_up_find(node, lambda node: node.type == "heading"):
            return True
        elif node.type == "text":
            match = process.extractOne(
                query=node.content, choices=highlights, scorer=fuzz.partial_ratio
            )
            return match and match[1] > FUZZY_MATCH_MIN_SCORE
        return False

    def descendant_has_text_or_is_heading(node: SyntaxTreeNode):
        for current in node.walk():
            if current.type == "text" or walk_up_find(
                node, lambda node: node.type == "heading"
            ):
                return True
        return False

    # Test the filter_syntax_tree function with the sample tree and evaluation function
    while num_removed := filter_syntax_tree(
        syntax_tree, partially_matches_highlight_or_heading
    ):
        print(f"Removed {num_removed} nodes filter 1")
    while num_removed := filter_syntax_tree(
        syntax_tree, descendant_has_text_or_is_heading
    ):
        print(f"Removed {num_removed} nodes filter 2")

    # Ensure that the filtered syntax tree contains only heading nodes
    resulting_markdown = MDRenderer().render(syntax_tree.to_tokens(), mdit.options, env)
    return resulting_markdown


def save_markdown_to_file(markdown, output_file):
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(markdown)


def remove_location_links(highlights):
    # Define a regex pattern to match the location links at the end of a string
    pattern = r"\s*\(\[Location\s+\d+\]\(.*?\)\)"

    # Use re.sub to remove the location links from each highlight
    cleaned_highlights = [re.sub(pattern, "", highlight) for highlight in highlights]

    return cleaned_highlights


def remove_trailing_newlines(highlights):
    # Define a regex pattern to match trailing newline characters
    pattern = r"\n+$"

    # Use re.sub to remove trailing newlines from each highlight
    cleaned_highlights = [re.sub(pattern, "", highlight) for highlight in highlights]

    return cleaned_highlights


def extract_text_highlights(text):
    # Split the input text into highlights using regular expressions
    pattern = r"\(.*?\)\n\n"

    # Use re.findall to find all matches of the pattern in the input text
    highlights = re.split(pattern, input_text)

    # Remove the location links and leading/trailing whitespace from each match
    highlights = remove_location_links(highlights)
    highlights = remove_trailing_newlines(highlights)

    return highlights


def get_highlights_from_raw_text(highlights_raw_text):
    # Remove square brackets and their contents (e.g., [Location 2820])
    highlights = extract_text_highlights(highlights_raw_text)
    # sanitized_highlights = re.sub(r"\[.*?\]", "", highlights)

    # # Replace smart quotes with regular quotes
    # sanitized_highlights = (
    #     sanitized_highlights.replace("“", '"')
    #     .replace("”", '"')
    #     .replace("‘", "'")
    #     .replace("’", "'")
    # )

    # Split into paragraphs based on sentences
    # paragraphs = sent_tokenize(sanitized_highlights)

    # return paragraphs
    return highlights


if __name__ == "__main__":
    article_file_path = "article_sample.md"
    output_file = "data/output.md"
    input_file = "highlights_sample.md"
    # Read input from the input.md file
    input_text = ""
    article_text = ""
    with open(input_file, "r", encoding="utf-8") as file:
        input_text = file.read()
    highlights = get_highlights_from_raw_text(input_text)
    with open(article_file_path, "r", encoding="utf-8") as file:
        article_text = file.read()

    extracted_md = extract_highlights_from_md(article_text, highlights)
    save_markdown_to_file(extracted_md, output_file)

    print(f"Titles saved to {output_file}")
