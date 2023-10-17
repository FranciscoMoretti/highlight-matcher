from typing import Any, Callable

from markdown_it.tree import SyntaxTreeNode


# Function to traverse the syntax tree and filter nodes
def filter_syntax_tree(
    root_node: SyntaxTreeNode,
    filter_fn: Callable[[Any], bool],
):
    deleted_nodes = []
    for current_node in root_node.walk():
        if not filter_fn(current_node):
            deleted_nodes.append(current_node)
    for current_node in deleted_nodes:
        if parent := current_node.parent:
            parent.children.remove(current_node)
    return len(deleted_nodes)


def walk_up_find_node(node: SyntaxTreeNode, func):
    # Start with the current node
    current_node = node

    # Iterate through parent elements recursively
    while current_node is not None:
        # Apply the function to the current node
        result = func(current_node)

        # If the function returns True, stop and return True
        if result:
            return current_node

        # Move to the parent node
        current_node = current_node.parent

    # If we reach the last parent without the function returning True, return False
    return None


def walk_up_find(node: SyntaxTreeNode, func):
    # Start with the current node
    current_node = node

    # Iterate through parent elements recursively
    while current_node is not None:
        # Apply the function to the current node
        result = func(current_node)

        # If the function returns True, stop and return True
        if result:
            return True

        # Move to the parent node
        current_node = current_node.parent

    # If we reach the last parent without the function returning True, return False
    return False
