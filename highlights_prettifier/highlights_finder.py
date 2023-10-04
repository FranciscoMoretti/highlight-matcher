from markdown_it import MarkdownIt
from rapidfuzz import fuzz


# Define your evaluating function
def should_keep_node(node):
    # Example: Keep only heading nodes (h1, h2, h3, etc.)
    return node["type"] == "heading_open"


# Function to traverse the syntax tree and filter nodes
def filter_syntax_tree(node, parent=None):
    if should_keep_node(node):
        # If the node should be kept, add it to the parent node
        if parent is not None:
            parent.append(node)
        # Recursively process child nodes
        for child in node.get("children", []):
            filter_syntax_tree(child, node)
    else:
        # If the node should be discarded, remove it from its parent
        if parent is not None and "children" in parent:
            parent["children"].remove(node)


def find_highlight_text(highlights, book_content):
    # Initialize the markdown parser
    md = MarkdownIt()

    # Parse the book content into an abstract syntax tree (AST)
    ast = md.parse(book_content)

    def traverse_tree(node, highlight_index):
        if node["type"] == "text":
            # Sanitize the node's text and split it into sentences
            sanitized_text = node["content"].replace("\n", " ")
            sentences = [s.strip() for s in sanitized_text.split(".")]

            for sentence in sentences:
                for highlight in highlights[highlight_index:]:
                    # Use fuzzy matching to find the best match between the highlight
                    # and the sentence
                    ratio = fuzz.ratio(sentence.lower(), highlight.lower())
                    if ratio >= 80:  # Adjust the threshold as needed
                        return sentence

        if "children" in node:
            for child_node in node["children"]:
                result = traverse_tree(child_node, highlight_index)
                if result:
                    return result

        return None

    highlight_index = 0
    highlight_text = []

    # Traverse the AST to find highlight text
    for node in ast:
        result = traverse_tree(node, highlight_index)
        if result:
            highlight_text.append(result)
            highlight_index += 1

            # If all highlights are found, stop searching
            if highlight_index == len(highlights):
                break

    return "\n".join(highlight_text)
