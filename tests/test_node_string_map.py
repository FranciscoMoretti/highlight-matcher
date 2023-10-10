import pytest
from markdown_it.tree import SyntaxTreeNode
from highlights_prettifier.markdown_parser import MakdownParser
from highlights_prettifier.range import Range, substring_with_range
from highlights_prettifier.node_string_map import (
    NodeStringMap,
)


markdown_text_1 = """
Lorem Ipsum is **simply dummy** text of the printing
 and typesetting industry.
"""

markdown_text_2 = """
expose order objects.

#### The Law of Demeter

People often talk about something
"""


@pytest.mark.parametrize(
    "input_md, expected_string, expected_links_content",
    [
        (
            "This is\n a test.",
            "This is a test.",
            ["This is", " ", "a test."],
        ),
        (
            markdown_text_1,
            "Lorem Ipsum is simply dummy text of the printing and typesetting industry.",
            [
                "Lorem Ipsum is ",
                "simply dummy",
                " text of the printing",
                " ",
                "and typesetting industry.",
            ],
        ),
        (
            markdown_text_2,
            "expose order objects. The Law of Demeter People often talk about something",
            [
                "expose order objects.",
                " ",
                "The Law of Demeter",
                " ",
                "People often talk about something",
            ],
        ),
    ],
)
def test_node_string_map(input_md, expected_string, expected_links_content):
    parser = MakdownParser()
    tokens = parser.text_to_tokens(input_md)
    syntax_tree = parser.tokens_to_syntax_tree(tokens)

    node_string_map = NodeStringMap(syntax_tree)
    assert node_string_map.string == expected_string
    links_content = [
        substring_with_range(node_string_map.string, link.range)
        for link in node_string_map.links
    ]
    assert links_content == expected_links_content
