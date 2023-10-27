from dataclasses import dataclass


@dataclass
class Clipping:
    book_title: str
    page: str
    location: str
    date: str
    text: str
