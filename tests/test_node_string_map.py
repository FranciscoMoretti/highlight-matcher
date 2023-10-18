import pytest

from highlights_prettifier.markdown_parser import MarkdownParser
from highlights_prettifier.node_string_map import (
    NodeStringMap,
)
from highlights_prettifier.range import substring_by_range

markdown_text_1 = """
Lorem Ipsum is **simply dummy** text of the printing
 and typesetting industry.
"""

markdown_text_2 = """
expose order objects.

#### The Law of Demeter

People often talk about something
"""

markdown_text_3 = """
In Topic 8, [​*The Essence of Good
Design*​](#f_0026.xhtml#essence_of_design) we claim
"""

markdown_text_4 = """
|        |                                                 |
|--------|-------------------------------------------------|
| Tip 14 | Good Design Is Easier to Change Than Bad Design |
"""

markdown_text_5 = """

  - Stay current  
    Read news and posts online on technology different from that of your
    current project.
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
                "The Law of Demeter",
                "People often talk about something",
            ],
        ),
        (
            markdown_text_3,
            "In Topic 8, \u200bThe Essence of Good Design\u200b we claim",
            [
                "In Topic 8, ",
                "\u200b",  # empty whitespace char
                "The Essence of Good",
                " ",
                "Design",
                "\u200b",
                " we claim",
            ],
        ),
        (
            markdown_text_4,
            "Tip 14 Good Design Is Easier to Change Than Bad Design",
            ["Tip 14", "Good Design Is Easier to Change Than Bad Design"],
        ),
        (
            markdown_text_5,
            "Stay current Read news and posts online on technology different from that of your current project.",
            [
                "Stay current",
                " ",
                "Read news and posts online on technology different from that of your",
                " ",
                "current project.",
            ],
        ),
    ],
)
def test_node_string_map(input_md, expected_string, expected_links_content):
    parser = MarkdownParser()
    tokens = parser.text_to_tokens(input_md)
    syntax_tree = parser.tokens_to_syntax_tree(tokens)

    node_string_map = NodeStringMap(syntax_tree)
    assert node_string_map.string == expected_string
    links_content = [
        substring_by_range(node_string_map.string, link.range)
        for link in node_string_map.links
    ]
    assert links_content == expected_links_content
