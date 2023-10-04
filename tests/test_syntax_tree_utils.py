import markdown_it
from markdown_it.tree import SyntaxTreeNode
from mdformat.renderer import MDRenderer

from ..highlights_prettifier.syntax_tree_utils import filter_syntax_tree


def test_filter_syntax_tree():
    # Parse Markdown content into a syntax tree
    mdit = markdown_it.MarkdownIt()
    env = {}
    markdown_content = "## Header 1\nSome text\n### Header 2\nMore text"
    tokens = mdit.parse(markdown_content, env)

    syntax_tree = SyntaxTreeNode(tokens)
    # Create a dummy root node to hold the filtered nodes

    # Define a simple evaluation function to keep heading nodes
    def should_keep_node(node: SyntaxTreeNode):
        return (node.children and node.type != "text") or (
            node.type == "text" and node.content == "Header 2"
        )

    def descendant_has_text(node: SyntaxTreeNode):
        for current in node.walk():
            if current.type == "text":
                return True
        return False

    # Test the filter_syntax_tree function with the sample tree and evaluation function
    while num_removed := filter_syntax_tree(syntax_tree, should_keep_node):
        print(f"Removed {num_removed} nodes")
    filter_syntax_tree(syntax_tree, descendant_has_text)

    # Ensure that the filtered syntax tree contains only heading nodes
    resulting_markdown = MDRenderer().render(syntax_tree.to_tokens(), mdit.options, env)
    assert resulting_markdown == "### Header 2\n"
