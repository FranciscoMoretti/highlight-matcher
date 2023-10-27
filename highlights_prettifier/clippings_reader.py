from typing import List
import re

from highlights_prettifier.clipping import Clipping


def save_clippings_to_file(clippings, output_file):
    with open(output_file, "w", encoding="utf-8") as file:
        for clipping in clippings:
            file.write(f"{clipping.text}\n\n")


def extract_clippings(file_path) -> List[Clipping]:
    clippings = []

    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()
        clipping_sections = re.split(r"==========\n", content)

        for section in clipping_sections:
            lines = section.strip().split("\n")

            if len(lines) < 4:
                print("Incomplete section")
                print(lines)
                continue

            # Extract book title
            book_title = lines[0].strip()

            # Extract page, location, date
            meta_info = lines[1].strip()
            match = re.search(
                r"^(?:- Your Highlight on page (\d+) \| )?location (\d+)-\d+ \| Added on (.+)$",
                meta_info,
            )
            page, location, date = match.groups() if match else (None, None, None)

            # Extract the highlighted text
            text = "\n".join(lines[2:])
            if "<You have reached the clipping limit for this item>" in text:
                continue

            # Create a Clipping object and add it to the list
            clipping = Clipping(book_title, page, location, date, text)
            clippings.append(clipping)

    return clippings


# Usage
file_path = "data/My Clippings.txt"
book = "The Pragmatic Programmer: your journey to mastery, 20th Anniversary Edition, 2nd Edition (David Thomas;Andrew Hunt)"

clippings = extract_clippings(file_path)

# Print the extracted clippings
books = list(set(clipping.book_title for clipping in clippings))
# Print books
for book_title in books:
    print(book_title)

book_clippings = [clipping for clipping in clippings if clipping.book_title == book]

save_clippings_to_file(clippings=book_clippings, output_file="data/book_clippings.txt")
