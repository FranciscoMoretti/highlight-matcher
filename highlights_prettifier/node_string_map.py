from dataclasses import dataclass
from itertools import tee
from markdown_it.tree import SyntaxTreeNode

from highlights_prettifier.range import Range


@dataclass
class NodeStringLink:
    node: SyntaxTreeNode
    range: Range


class NodeStringMap:
    def __init__(self, root_node: SyntaxTreeNode):
        self.string = ""
        self.links = []
        self._build_map_conections(root_node)

    def _build_map_conections(self, root_node):
        start_index = 0
        end_index = 0
        for node in root_node.walk():
            if node.type == "text":
                stringifyied = node.content
            elif node.type in ["softbreak", "paragraph", "heading"]:
                stringifyied = " "
            else:
                continue
            start_index = len(self.string)
            end_index = start_index + len(stringifyied)

            if start_index == 0 and stringifyied == " ":
                continue

            self.string += stringifyied
            self.links.append(
                NodeStringLink(
                    node=node, range=Range(start_pos=start_index, end_pos=end_index)
                )
            )
