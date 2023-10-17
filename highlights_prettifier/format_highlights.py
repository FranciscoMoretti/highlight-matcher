"""Main module."""
from typing import List

from markdown_it.tree import SyntaxTreeNode

from highlights_prettifier.highlight_finder import (
    fuzzy_find_substrings_sequence,
)
from highlights_prettifier.markdown_parser import MarkdownParser
from highlights_prettifier.node_string_map import NodeStringLink, NodeStringMap
from highlights_prettifier.range import (
    Range,
    calculate_overlap,
    substring_by_range,
)
from highlights_prettifier.status import Status
from highlights_prettifier.status_tree import StatusTree, set_node_status
from highlights_prettifier.syntax_tree_utils import walk_up_find


def filter_node_string_links(
    node_links: List[NodeStringLink], filter_ranges: List[Range]
) -> List[NodeStringLink]:
    filtered_list = []
    node_idx, range_idx = 0, 0  # Index variables for node_links and filter_ranges

    while node_idx < len(node_links) and range_idx < len(filter_ranges):
        node_link = node_links[node_idx]
        filter_range = filter_ranges[range_idx]

        if node_link.range.end_pos < filter_range.start_pos:
            # If node_link is completed before filter_range, advance node_link
            node_idx += 1
        elif node_link.range.start_pos > filter_range.end_pos:
            # If node_link is completed after filter_range, advance filter_range
            range_idx += 1
        else:
            # If there is an overlap, add node_link to the filtered list
            overlap_range = calculate_overlap(node_link.range, filter_range)
            _filter_node_text_with_range(node_link, overlap_range)
            filtered_list.append(node_link)
            node_idx += 1  # Move to the next node_link, as ranges do not overlap

    return filtered_list


def _filter_node_text_with_range(node_link, overlap_range):
    overlap_relative_to_node = Range(
        overlap_range.start_pos - node_link.range.start_pos,
        overlap_range.end_pos - node_link.range.start_pos,
    )
    print(
        "Filtered content: "
        f"{substring_by_range(node_link.node.content, overlap_relative_to_node)}"
    )
    overlap_text = node_link.node.content[
        overlap_relative_to_node.start_pos : overlap_relative_to_node.end_pos
    ]
    # TODO: Handle the scenario of potentially many highlights in a single node token
    # In the current implementation, the last highlight replaces all the text.
    # to solve this process all nodes from the range at the same time
    if node_link.node.token:
        node_link.node.token.content = overlap_text
        node_link.range = overlap_range


def create_formated_highlights(article_text, highlights):
    # Create a dummy root node to hold the filtered nodes
    parser = MarkdownParser()
    tokens = parser.text_to_tokens(article_text)
    syntax_tree = parser.tokens_to_syntax_tree(tokens)

    for node in syntax_tree.walk():
        set_node_status(node, Status.TO_BE_REMOVED)

    status_tree = StatusTree(root_node=syntax_tree)

    node_strings_map = NodeStringMap(root_node=syntax_tree)

    highlihgt_matches_ranges = list(
        fuzzy_find_substrings_sequence(node_strings_map.string, highlights)
    )
    for match_range in highlihgt_matches_ranges:
        print(
            "Matched strings: "
            f"{substring_by_range(string=node_strings_map.string, range=match_range)}"
        )

    # TODO: Investigate problem of missing whitespaces
    matched_node_links = filter_node_string_links(
        node_links=node_strings_map.links,
        filter_ranges=highlihgt_matches_ranges,
    )
    for link in matched_node_links:
        print(
            "Matched text: "
            f"{substring_by_range(string=node_strings_map.string, range=link.range)}"
        )
    matched_nodes = [node_link.node for node_link in matched_node_links]

    findings = status_tree.find_nodes_with_content("is the enemy of change")

    def ascendant_is_heading(node: SyntaxTreeNode):
        return walk_up_find(node, lambda node: node.type == "heading")

    # TODO: Program removes code from some of the headings

    num_updated = status_tree.update_status(
        should_update=lambda node: node in matched_nodes,
        new_status=Status.ENABLED,
    )
    print(f"Updated {num_updated} nodes filter 1")

    num_updated = status_tree.update_status(
        should_update=ascendant_is_heading, new_status=Status.ENABLED
    )
    print(f"Updated {num_updated} nodes filter 2")

    while num_removed := status_tree.perform_removals():
        print(f"Remmoved {num_removed} nodes")

    # TODO: Removal doesn't remove tokens or content from ancester nodes
    # and content is not filtered correctly

    # Ensure that the filtered syntax tree contains only heading nodes
    resulting_markdown = parser.syntax_tree_to_text(syntax_tree)
    return resulting_markdown
