from dataclasses import dataclass
from typing import Callable
from uu import Error

from markdown_it.tree import SyntaxTreeNode

from highlights_prettifier.status import Status
from highlights_prettifier.syntax_tree_utils import walk_up_find_node


def node_has_status(node: SyntaxTreeNode):
    """
    Returns a node status
    """
    return get_node_status(node) != Status.NO_STATUS


def get_node_status(node: SyntaxTreeNode):
    """
    Returns a node status
    """
    if node.token and (status := node.token.meta.get("status")):
        return status
    return Status.NO_STATUS


def set_node_status(node: SyntaxTreeNode, status: Status):
    """
    Sets a node status
    """
    if node.token:
        node.token.meta["status"] = status


@dataclass
class StatusTree:
    root_node: SyntaxTreeNode

    def update_status(
        self, should_update: Callable[[SyntaxTreeNode], bool], new_status: Status
    ) -> int:
        num_updated = 0
        for node in self.root_node.walk():
            if should_update(node):
                if node_has_status(node):
                    if get_node_status(node) != new_status:
                        set_node_status(node, new_status)
                        num_updated += 1
        return num_updated

    def perform_removals(self) -> int:
        self._mark_ascendants_as_enabled()
        # sorted_nodes = self._walk_nodes_leafs_to_root()
        nodes_to_remove = list(
            filter(
                lambda node: get_node_status(node) == Status.TO_BE_REMOVED,
                self.root_node.walk(),
            )
        )
        self._remove_nodes(nodes_to_remove)
        nodes_no_children = list(
            filter(
                lambda node: (
                    get_node_status(node) != Status.ENABLED and len(node.children) == 0
                ),
                self.root_node.walk(),
            )
        )
        self._remove_nodes(nodes_no_children)

        self._update_ascendants_content()
        return len(nodes_to_remove) + len(nodes_no_children)

    def find_nodes_with_content(self, content: str):
        return list(
            filter(
                lambda node: content in node.content
                if hasattr(node, "content")
                else False,
                self.root_node.walk(),
            )
        )

    def _remove_nodes(self, nodes_to_remove):
        for node in nodes_to_remove:
            if parent := node.parent:
                if node.token is not None:
                    self._remove_token(node.token, parent)
                if node.is_nested and node.nester_tokens.closing is not None:
                    self._remove_token(node.nester_tokens.closing, parent)
                if node.is_nested and node.nester_tokens.opening is not None:
                    self._remove_token(node.nester_tokens.opening, parent)

                parent.children.remove(node)
                # node.status = Status.REMOVED  # Already removed
            else:
                raise Error("Attempted to remove node without parent")

    def _remove_token(self, token, parent):
        if token is not None:
            ancestor_with_token = walk_up_find_node(
                parent,
                lambda node: node.token is not None and node.token.children,
            )
            if ancestor_with_token is not None:
                ancestor_with_token.token.children.remove(token)

    def _mark_ascendants_as_enabled(self):
        enabled_nodes = [
            node
            for node in self.root_node.walk()
            if get_node_status(node) == Status.ENABLED
        ]
        for node in enabled_nodes:
            while node.parent is not None:
                if get_node_status(node.parent) not in [
                    Status.ENABLED,
                    Status.NO_STATUS,
                ]:
                    set_node_status(node.parent, Status.ENABLED)
                node = node.parent

    def _update_ascendants_content(self):
        remaining_nodes = self._walk_nodes_leafs_to_root()
        # for start_node in remaining_nodes:
        #     node = start_node
        #     while node is not None:
        #         if (
        #             hasattr(node, "content")
        #             and node.token
        #             and node.token.content
        #             and node.children
        #         ):
        #             node.token.content = " ".join(
        #                 subnode.content
        #                 for subnode in node.children
        #                 if hasattr(subnode, "content")
        #             )
        #         node = node.parent

    def _walk_nodes_leafs_to_root(self):
        return sorted(
            list(self.root_node.walk()),
            key=lambda node: node.level if hasattr(node, "level") else -1,
            reverse=True,
        )
