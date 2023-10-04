import re


def remove_location_links(highlights):
    # Define a regex pattern to match the location links at the end of a string
    pattern = r"\s*\(\[Location\s+\d+\]\(.*?\)\)"

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
    # Split the input text into highlights using regular expressions
    pattern = r"\(.*?\)\n\n"

    # Use re.findall to find all matches of the pattern in the input text
    highlights = re.split(pattern, input_text)

    # Remove the location links and leading/trailing whitespace from each match
    highlights = remove_location_links(highlights)
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

    # Split into paragraphs based on sentences
    # paragraphs = sent_tokenize(sanitized_highlights)

    # return paragraphs
    return highlights
