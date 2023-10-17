from typing import List

from markdown_it import MarkdownIt
from markdown_it.token import Token
from markdown_it.tree import SyntaxTreeNode


class MarkdownParser:
    """
    docstring
    """

    def __init__(self):
        self.mdit = MarkdownIt("gfm-like")
        # TODO Parse github markdown better?
        self.env = {}

    def text_to_tokens(self, text) -> List[Token]:
        return self.mdit.parse(text, self.env)

    def tokens_to_syntax_tree(self, tokens) -> SyntaxTreeNode:
        return SyntaxTreeNode(tokens)

    def syntax_tree_to_text(self, syntax_tree):
        return self.mdit.renderer.render(
            syntax_tree.to_tokens(), self.mdit.options, self.env
        )
