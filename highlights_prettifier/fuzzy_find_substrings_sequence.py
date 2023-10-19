from typing import List
from uu import Error

from rapidfuzz import fuzz
from highlights_prettifier.refine_matching import refine_matching
from highlights_prettifier.default_tuning import (
    FUZZY_APROXIMATION_MIN_SCORE,
    FUZZY_MATCH_MIN_SCORE,
)

from highlights_prettifier.range import (
    Range,
    extend_substring_range,
    substring_by_range,
)


SEARCH_WINDOW_FACTOR = 2


# TODO: Highlight matching has to be stripped. whitespaces can mean breaks, paragraphs or titles
def fuzzy_find_substrings_sequence(
    long_string: str, substrings: List[str], raise_errors=False, min_chars=6
):
    current_start = 0
    for needle in substrings:
        if len(needle) < min_chars:
            # TODO: say highlight to short and report
            continue
        # Extend window until first alignment
        first_alignment_range = _find_first_alignment_range(
            long_string, needle, current_start
        )
        if first_alignment_range is None:
            if raise_errors:
                raise Error("First alignment failed")
            else:
                continue

        refinement_search_range = _get_search_range_around_alignment(
            long_string, first_alignment_range
        )
        refined_match_string = refine_matching(
            hay=substring_by_range(long_string, refinement_search_range), needle=needle
        )
        if not refined_match_string:
            if raise_errors:
                raise Error("Match Refinement Failed but basic alignment worked")
            else:
                continue
        # Rematch to find the index with the string extracted from current hay
        alignment_range = _get_full_alignment_range(
            string=substring_by_range(long_string, refinement_search_range),
            substring=refined_match_string,
        )
        if alignment_range is not None:
            alignment_range = alignment_range.offset(refinement_search_range.start_pos)
            yield alignment_range

            current_start = alignment_range.end_pos


def _get_full_alignment_range(string, substring):
    alignment = fuzz.partial_ratio_alignment(
        s1=string,
        s2=substring,
        score_cutoff=FUZZY_MATCH_MIN_SCORE,
    )
    if alignment is not None:
        return Range(alignment.src_start, alignment.src_end)
    return None


def _find_first_alignment_range(long_string, substring, current_start=0):
    search_range = Range(start_pos=current_start, end_pos=current_start)
    # TODO: Window selection can be enough to align without having the complete substring
    # A better algorithm needs to be found
    window_length = len(substring) * SEARCH_WINDOW_FACTOR
    partial_alignment_range = None
    while partial_alignment_range is None:
        # Extend the search end limit
        search_range.end_pos = min(
            search_range.end_pos + window_length, len(long_string)
        )

        partial_alignment_range = _get_alignment_range_in_search_range(
            hay=long_string,
            needle=substring,
            search_range=search_range,
            score_cutoff=FUZZY_APROXIMATION_MIN_SCORE,
        )
        if partial_alignment_range is None and search_range.end_pos == len(long_string):
            # Reached the end without finding, try being more permisive
            partial_alignment_range = _get_alignment_range_in_search_range(
                hay=substring_by_range(long_string, search_range),
                needle=substring,
                search_range=search_range,
                score_cutoff=FUZZY_APROXIMATION_MIN_SCORE - 10,
            )
            if not partial_alignment_range:
                # Give up without finding a match
                return None
    # Search again around the alignment to prevent boundary conditions
    # E.g. matching string missing one character because it search range end cut off
    search_range_around_partial_alignment = extend_substring_range(
        complete_string_len=len(long_string),
        extension_length=len(substring),
        substring_range=partial_alignment_range,
    )

    complete_alignment_range = _get_alignment_range_in_search_range(
        hay=long_string,
        needle=substring,
        search_range=search_range_around_partial_alignment,
        score_cutoff=FUZZY_APROXIMATION_MIN_SCORE,
    )

    return complete_alignment_range


def _get_alignment_range_in_search_range(
    hay, needle, search_range: Range, score_cutoff: float
):
    alignment = fuzz.partial_ratio_alignment(
        substring_by_range(hay, search_range),
        needle,
        score_cutoff=score_cutoff,
    )
    if alignment:
        return Range(
            alignment.src_start,
            alignment.src_end,
        ).offset(search_range.start_pos)
    return None


def _get_search_range_around_alignment(
    current_hay: str, alignment_range: Range
) -> Range:
    extended_range = extend_substring_range(
        complete_string_len=len(current_hay),
        substring_range=alignment_range,
        extension_length=int(
            0.2 * (alignment_range.end_pos - alignment_range.start_pos) + 10
        ),
    )
    return extended_range
