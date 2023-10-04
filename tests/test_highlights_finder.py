from ..highlights_prettifier.syntax_tree import filter_syntax_tree, walk_up_find
from mdformat.renderer import MDRenderer
from markdown_it import MarkdownIt
from rapidfuzz import fuzz, process
from markdown_it.tree import SyntaxTreeNode
import pytest


highlights_0 = [
    "This is HTML abbreviation example",
    'keep intact partial entries like "xxxHTMLyyy"',
]

book_content_0 = """
### [Abbreviations](https://github.com/markdown-it/markdown-it-abbr)

This is HTML abbreviation example.

It converts "HTML", but keep intact partial entries like "xxxHTMLyyy" and so on.

[HTML]: Hyper Text Markup Language

"""

expected_filtered_content_0 = '### [Abbreviations](https://github.com/markdown-it/markdown-it-abbr)\n\nThis is HTML abbreviation example.\n\nIt converts "HTML", but keep intact partial entries like "xxxHTMLyyy" and so on.\n'


book_content_1 = """
Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt
ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation
ullamco laboris nisi ut aliquip ex ea commodo consequat.

"""
highlights_1 = [
    "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.",
]

expected_filtered_content_1 = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt\nut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation\nullamco laboris nisi ut aliquip ex ea commodo consequat.\n"

FUZZY_MATCH_MIN_SCORE = 80


def test_find_highlight_paragraphs():
    mdit = MarkdownIt()
    env = {}
    tokens = mdit.parse(book_content_0, env)

    syntax_tree = SyntaxTreeNode(tokens)
    # Create a dummy root node to hold the filtered nodes

    # Define a simple evaluation function to keep heading nodes
    def partially_matches_highlight(node: SyntaxTreeNode):
        if node.children:
            return True
        elif node.type == "text":
            match = process.extractOne(
                query=node.content, choices=highlights_0, scorer=fuzz.partial_ratio
            )
            return match and match[1] > FUZZY_MATCH_MIN_SCORE
        return False

    def descendant_has_text(node: SyntaxTreeNode):
        for current in node.walk():
            if current.type == "text":
                return True
        return False

    # Test the filter_syntax_tree function with the sample tree and evaluation function
    while num_removed := filter_syntax_tree(syntax_tree, partially_matches_highlight):
        print(f"Removed {num_removed} nodes")
    filter_syntax_tree(syntax_tree, descendant_has_text)

    # Ensure that the filtered syntax tree contains only heading nodes
    resulting_markdown = MDRenderer().render(syntax_tree.to_tokens(), mdit.options, env)
    assert (
        resulting_markdown
        == "## Images\n\nLike links, Images also have a footnote style syntax"
        "\n\nWith a reference later in the document defining the URL location:\n"
    )


@pytest.mark.parametrize(
    "book_content, highlights, expected_resulting_markdown",
    [
        pytest.param(
            book_content_0,
            highlights_0,
            expected_filtered_content_0,
            id="some_chapter_0",
        ),
        pytest.param(
            book_content_1,
            highlights_1,
            expected_filtered_content_1,
            id="some_chapter_1",
        ),
    ],
)
def test_find_highlight_and_titles(
    book_content, highlights, expected_resulting_markdown
):
    mdit = MarkdownIt()
    env = {}
    tokens = mdit.parse(book_content, env)

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
        print(f"Removed {num_removed} nodes")
    filter_syntax_tree(syntax_tree, descendant_has_text_or_is_heading)

    # Ensure that the filtered syntax tree contains only heading nodes
    resulting_markdown = MDRenderer().render(syntax_tree.to_tokens(), mdit.options, env)
    assert resulting_markdown == expected_resulting_markdown
