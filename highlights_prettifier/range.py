from dataclasses import dataclass
from typing import Optional


@dataclass
class Range:
    start_pos: int
    end_pos: int


def calculate_overlap(range1: Range, range2: Range) -> Optional[Range]:
    """
    Calculate the overlap between two ranges.

    Args:
        range1 (Range): The first range.
        range2 (Range): The second range.

    Returns:
        Range or None: The overlapping range, or None if there is no overlap.
    """
    overlap_start = max(range1.start_pos, range2.start_pos)
    overlap_end = min(range1.end_pos, range2.end_pos)

    if overlap_start <= overlap_end:
        return Range(overlap_start, overlap_end)
    else:
        return None


def substring_with_range(string: str, range: Range) -> str:
    return string[range.start_pos : range.end_pos]


def extend_substring_range(
    complete_string_len: int, substring_range: Range, extension_length: int = 10
):
    start_pos = max(substring_range.start_pos - extension_length, 0)
    end_pos = min(substring_range.end_pos + extension_length, complete_string_len)

    return Range(start_pos, end_pos)
