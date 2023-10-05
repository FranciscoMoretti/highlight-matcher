"""Main module."""
from typing import Callable, List
from uu import Error
from attr import dataclass
import nltk
from dataclasses import dataclass

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

    # Define a simple evaluation function to keep heading nodes
    def partially_matches_highlight_or_heading(node: SyntaxTreeNode):
        if walk_up_find(node, lambda node: node.type == "heading"):
            return True
        elif node.type == "text":
            match = process.extractOne(
                query=node.content, choices=highlights, scorer=fuzz.partial_ratio
            )
            return match and match[1] > FUZZY_MATCH_MIN_SCORE
        return False

    def ascendant_is_heading(node: SyntaxTreeNode):
        for current in node.walk():
            if walk_up_find(current, lambda node: node.type == "heading"):
                return True
        return False

    while num_removed := status_tree.update_status(
        should_update=partially_matches_highlight_or_heading, new_status=Status.ENABLED
    ):
        print(f"Updated {num_removed} nodes filter 1")

    while num_removed := status_tree.update_status(
        should_update=ascendant_is_heading, new_status=Status.ENABLED
    ):
        print(f"Updated {num_removed} nodes filter 2")

    while num_removed := status_tree.perform_removals():
        print(f"Remmoved {num_removed} nodes")

    # Ensure that the filtered syntax tree contains only heading nodes
    resulting_markdown = parser.syntax_tree_to_text(syntax_tree)
    return resulting_markdown
