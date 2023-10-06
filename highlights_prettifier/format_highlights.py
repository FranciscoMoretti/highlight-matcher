"""Main module."""
from typing import Callable, List
from uu import Error
from attr import dataclass
import nltk
from dataclasses import dataclass
from highlight_finder import find_substrings_sequence
from range import Range, calculate_overlap

from syntax_tree_utils import filter_syntax_tree, walk_up_find
from mdformat.renderer import MDRenderer
from markdown_it import MarkdownIt
from rapidfuzz import fuzz, process
from markdown_it.tree import SyntaxTreeNode
from enum import Enum

# nltk.download("punkt")

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


class Status(Enum):
    ENABLED = 1  # Nodes that are currently enabled or active.
    DISABLED = 2  # Nodes that are currently disabled or inactive.
    TO_BE_REMOVED = (
        3  # Nodes that are marked for removal but have not been removed yet.
    )
    REMOVED = 4  # Nodes that have been removed and should not be considered in the list anymore.


@dataclass
class NodeStatus:
    node: SyntaxTreeNode
    status: Status


@dataclass
class NodeStringConnection:
    node: SyntaxTreeNode
    range: Range


def filter_node_string_connections(
    node_connections: List[NodeStringConnection], filter_ranges: List[Range]
) -> List[NodeStringConnection]:
    filtered_list = []
    node_idx, range_idx = 0, 0  # Index variables for node_connections and filter_ranges

    while node_idx < len(node_connections) and range_idx < len(filter_ranges):
        node_connection = node_connections[node_idx]
        filter_range = filter_ranges[range_idx]

        if node_connection.range.end_pos < filter_range.start_pos:
            # If node_connection is completed before filter_range, advance node_connection
            node_idx += 1
        elif node_connection.range.start_pos > filter_range.end_pos:
            # If node_connection is completed after filter_range, advance filter_range
            range_idx += 1
        else:
            # If there is an overlap, add node_connection to the filtered list
            overlap_range = calculate_overlap(node_connection.range, filter_range)
            _filter_node_text_with_range(node_connection, overlap_range)
            filtered_list.append(node_connection)
            node_idx += 1  # Move to the next node_connection, as ranges do not overlap

    return filtered_list


def _filter_node_text_with_range(node_connection, overlap_range):
    overlap_relative_to_node = Range(
        overlap_range.start_pos - node_connection.range.start_pos,
        overlap_range.end_pos - node_connection.range.start_pos,
    )
    overlap_text = node_connection.node.content[
        overlap_relative_to_node.start_pos : overlap_relative_to_node.end_pos
    ]
    node_connection.node.token.content = overlap_text


class NodeStringMap:
    def __init__(self, root_node: SyntaxTreeNode):
        self.string = ""
        self.connections = []
        self._build_map_conections(root_node)

    def _build_map_conections(self, root_node):
        text_nodes = [node for node in root_node.walk() if node.type == "text"]
        start_index = 0
        end_index = 0
        for node in text_nodes:
            start_index = len(self.string)
            end_index = start_index + len(node.content)
            self.string += node.content + " "
            self.connections.append(
                NodeStringConnection(
                    node=node, range=Range(start_pos=start_index, end_pos=end_index)
                )
            )


@dataclass
class NodeStatusTree:
    root_node: SyntaxTreeNode
    nodes_status_list: List[NodeStatus]

    def update_status(
        self, should_update: Callable[[SyntaxTreeNode], bool], new_status: Status
    ) -> int:
        num_updated = 0
        for current in self.root_node.walk():
            if should_update(current):
                node_status = self._find_node_status_of_node(current)
                if node_status.status != new_status:
                    node_status.status = new_status
                    num_updated += 1
        return num_updated

    def _find_node_status_of_node(self, current):
        return next((el for el in self.nodes_status_list if el.node == current))

    def perform_removals(self) -> int:
        self._mark_ascendants_as_enabled()
        nodes_to_remove = list(
            filter(
                lambda node_status: node_status.status == Status.TO_BE_REMOVED,
                self.nodes_status_list,
            )
        )
        for current_node_status in nodes_to_remove:
            if parent := current_node_status.node.parent:
                parent.children.remove(current_node_status.node)
                current_node_status.status = Status.REMOVED
            else:
                raise Error("Attempted to remove node without parent")
        return len(nodes_to_remove)

    def _mark_ascendants_as_enabled(self):
        enabled_node_statuses = [
            el for el in self.nodes_status_list if el.status == Status.ENABLED
        ]
        for enabled_node_status in enabled_node_statuses:
            current_node_status = enabled_node_status
            while current_node_status.node.parent is not None:
                if current_node_status.status != Status.ENABLED:
                    current_node_status.status = Status.ENABLED
                current_node_status = self._find_node_status_of_node(
                    current_node_status.node.parent
                )


def create_formated_highlights(article_text, highlights):
    # Create a dummy root node to hold the filtered nodes
    parser = MakdownParser()
    syntax_tree = parser.text_to_syntax_tree(article_text)

    node_status_list: List[NodeStatus] = [
        NodeStatus(node=node, status=Status.TO_BE_REMOVED)
        for node in syntax_tree.walk()
    ]
    node_status_list[0].status = Status.ENABLED  # Keep the root node

    status_tree = NodeStatusTree(
        root_node=syntax_tree, nodes_status_list=node_status_list
    )

    node_strings_map = NodeStringMap(root_node=syntax_tree)

    # TODO: Replace filter functions with matched_nodes
    highlihgt_matches_positions = list(
        find_substrings_sequence(node_strings_map.string, highlights)
    )

    for range in highlihgt_matches_positions:
        print(node_strings_map.string[range.start_pos : range.end_pos])

    matched_node_conections = filter_node_string_connections(
        node_connections=node_strings_map.connections,
        filter_ranges=highlihgt_matches_positions,
    )
    matched_nodes = [
        node_connection.node for node_connection in matched_node_conections
    ]

    def ascendant_is_heading(node: SyntaxTreeNode):
        return walk_up_find(node, lambda node: node.type == "heading")

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

    # Ensure that the filtered syntax tree contains only heading nodes
    resulting_markdown = parser.syntax_tree_to_text(syntax_tree)
    return resulting_markdown

    # def partially_matches_highlight(node: SyntaxTreeNode):
    #     if node.type == "text":
    #         match = process.extractOne(
    #             query=node.content, choices=highlights, scorer=fuzz.partial_ratio
    #         )
    #         return match and match[1] > FUZZY_MATCH_MIN_SCORE
    #     return False
