import re


def remove_location_links(highlights):
    # Define a regex pattern to match the location links at the end of a string
    pattern = r"\s*\(\[Location\s+\d+\]\(.*?\)\)"

    # Use re.sub to remove the location links from each highlight
    cleaned_highlights = [re.sub(pattern, "", highlight) for highlight in highlights]

    return cleaned_highlights


def remove_view_highlight_links(highlights):
    # Define a regex pattern to match the location links at the end of a string
    pattern = r"\s*\(\[View Highlight\]\(.*?\)\)"

    # Use re.sub to remove the location links from each highlight
    cleaned_highlights = [re.sub(pattern, "", highlight) for highlight in highlights]

    return cleaned_highlights


def remove_trailing_newlines(highlights):
    # Define a regex pattern to match trailing newline characters
    pattern = r"\n+$"

    # Use re.sub to remove trailing newlines from each highlight
    cleaned_highlights = [re.sub(pattern, "", highlight) for highlight in highlights]

    return cleaned_highlights


def extract_text_highlights(input_text):
    # Split the text into strings separated by empty lines
    split_strings = re.split(r"\n\s*\n", input_text)

    # Clean up the split strings by removing leading and trailing whitespace
    highlights = [s.strip() for s in split_strings if s.strip()]

    # Remove the location links and leading/trailing whitespace from each match
    highlights = remove_location_links(highlights)
    highlights = remove_view_highlight_links(highlights)
    highlights = remove_trailing_newlines(highlights)

    return highlights


def get_highlights_from_raw_text(highlights_raw_text):
    # Remove square brackets and their contents (e.g., [Location 2820])
    highlights = extract_text_highlights(highlights_raw_text)
    # sanitized_highlights = re.sub(r"\[.*?\]", "", highlights)

    # # Replace smart quotes with regular quotes
    # sanitized_highlights = (
    #     sanitized_highlights.replace("“", '"')
    #     .replace("”", '"')
    #     .replace("‘", "'")
    #     .replace("’", "'")
    # )
    highlights = [highlight.strip() for highlight in highlights]

    # Split into paragraphs based on sentences
    # paragraphs = sent_tokenize(sanitized_highlights)

    # return paragraphs
    return highlights
