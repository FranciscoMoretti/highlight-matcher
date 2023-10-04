"""Main module."""
from ast import parse
from typing import Self
import nltk

from highlights_prettifier.syntax_tree_utils import filter_syntax_tree, walk_up_find
from mdformat.renderer import MDRenderer
from markdown_it import MarkdownIt
from rapidfuzz import fuzz, process
from markdown_it.tree import SyntaxTreeNode

nltk.download("punkt")

# Customize the fuzziness threshold
FUZZY_MATCH_MIN_SCORE = 90  # Adjust as needed


class MakdownParser:
    """
    docstring
    """

    def __init__(self):
        self.mdit = MarkdownIt()
        self.env = {}

    def text_to_syntax_tree(self, text) -> SyntaxTreeNode:
        tokens = self.mdit.parse(text, self.env)
        return SyntaxTreeNode(tokens)

    def syntax_tree_to_text(self, syntax_tree):
        resulting_markdown = MDRenderer().render(
            syntax_tree.to_tokens(), self.mdit.options, self.env
        )
        return resulting_markdown


def create_formated_highlights(article_text, highlights):
    # Create a dummy root node to hold the filtered nodes
    parser = MakdownParser()
    syntax_tree = parser.text_to_syntax_tree(article_text)

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
    resulting_markdown = parser.syntax_tree_to_text(syntax_tree)
    return resulting_markdown
