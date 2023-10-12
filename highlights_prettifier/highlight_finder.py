import difflib
import re
from typing import List
from uu import Error
from highlights_prettifier.range import (
    Range,
    extend_substring_range,
    substring_by_range,
)
from rapidfuzz import fuzz, process, utils
from nltk.util import ngrams

FUZZY_MATCH_MIN_SCORE = 90
FUZZY_APROXIMATION_MIN_SCORE = 80


def tokenize_from_text(text):
    # Tokenize the input string into words (tokens)
    # TODO: This operation is not safe for multiple whitespaces because it doesn't count
    # them and then it joins them with a single whitespace
    return text.split()


def untokenize_to_text(tokens):
    return " ".join(tokens)


SEARCH_WINDOW_FACTOR = 2


# TODO: Highlight matching has to be stripped. whitespaces can mean breaks, paragraphs or titles
def fuzzy_find_substrings_sequence(
    long_string: str, substrings: List[str], raiseErrors=False, min_chars=6
):
    current_start = 0
    for needle in substrings:
        if len(needle) < min_chars:
            continue
        # Extend window until first alignment
        first_alignment_range = _find_first_alignment_range(
            long_string, current_start, needle
        )
        if first_alignment_range is None:
            # TODO: Fail if no initial alignment
            if raiseErrors:
                raise Error("First alignment failed")
            else:
                continue

        refinement_search_range = _get_search_range_around_alignment(
            long_string, first_alignment_range
        )

        refinement_hay = substring_by_range(long_string, refinement_search_range)
        # TODO: Find the max ratio of both algorithms
        refined_match_string = refine_matching_sequences(refinement_hay, needle)
        if not refined_match_string:
            refined_match_string = refine_matching_tokens(refinement_hay, needle)
        if not refined_match_string:
            if raiseErrors:
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


def _find_first_alignment_range(long_string, current_start, substring):
    window_length = len(substring) * SEARCH_WINDOW_FACTOR
    # TODO: Window selection can be enough to align without having the complete substring
    # A better algorithm needs to be found
    first_alignment = None
    search_range = Range(start_pos=current_start, end_pos=current_start)
    current_hay = ""
    while first_alignment is None:
        # Extend the search end limit
        search_range.end_pos = min(
            search_range.end_pos + window_length, len(long_string)
        )

        current_hay = substring_by_range(long_string, search_range)
        first_alignment = fuzz.partial_ratio_alignment(
            current_hay,
            substring,
            score_cutoff=FUZZY_APROXIMATION_MIN_SCORE,
        )
        if first_alignment is None and search_range.end_pos == len(long_string):
            # Reached the end without finding, try being more permisive
            first_alignment = fuzz.partial_ratio_alignment(
                current_hay,
                substring,
                score_cutoff=FUZZY_APROXIMATION_MIN_SCORE - 10,
            )
            if not first_alignment:
                # Give up without finding a match
                return None
    return Range(
        first_alignment.src_start,
        first_alignment.src_end,
    ).offset(current_start)


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


def refine_matching_tokens(current_hay, substring):
    needle_length = len(substring.split())
    max_sim_val = 0
    max_sim_string = ""
    hay_tokens = tokenize_from_text(current_hay)

    # Todo consider less grams length
    for ngram in ngrams(hay_tokens, min(needle_length, len(hay_tokens))):
        hay_ngram = untokenize_to_text(ngram)
        # similarity = SM(None, hay_ngram, substring).ratio()
        similarity = fuzz.token_ratio(hay_ngram, substring)
        if similarity > max_sim_val and similarity > FUZZY_MATCH_MIN_SCORE:
            max_sim_val = similarity
            max_sim_string = hay_ngram
    return max_sim_string


def preprocess(seq):
    return utils.default_process(str(seq))


def refine_matching_sequences(hay, needle):
    # Tokenize the input strings
    matcher = difflib.SequenceMatcher(None, hay, needle)
    match_ranges_raw = matcher.get_matching_blocks()
    match_ranges = match_ranges_raw[:-1]  # Remove dummy last triple

    if len(match_ranges) == 0:
        return ""

    hay_end = match_ranges[-1].a + match_ranges[-1].size
    hay_start = match_ranges[0].a
    result = hay[hay_start:hay_end]

    return result
