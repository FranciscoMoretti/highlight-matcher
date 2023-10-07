from typing import List
from highlights_prettifier.range import Range, extend_substring_range
from rapidfuzz import fuzz
from difflib import SequenceMatcher as SM
from nltk.util import ngrams

FUZZY_MATCH_MIN_SCORE = 90
FUZZY_APROXIMATION_MIN_SCORE = 80


def find_substrings_sequence(long_string: str, substrings: List[str]):
    start = 0
    for substring in substrings:
        start_pos = long_string.find(substring, start)
        if start_pos == -1:
            # If the substring is not found, stop the generator
            break
        end_pos = start_pos + len(substring)
        yield Range(start_pos, end_pos)
        start = end_pos + 1


def tokenize_from_text(text):
    # Tokenize the input string into words (tokens)
    # TODO: This operation is not safe for multiple whitespaces because it doesn't count
    # them and then it joins them with a single whitespace
    return text.split()


def untokenize_to_text(tokens):
    return " ".join(tokens)


# Algorithm find in https://stackoverflow.com/questions/17740833/checking-fuzzy-approximate-substring-existing-in-a-longer-string-in-python
# Other alternatives in same question
def fuzzy_find_substrings_sequence(long_string: str, substrings: List[str]):
    current_start = 0
    current_hay = long_string

    for substring in substrings:
        first_alignment = fuzz.partial_ratio_alignment(
            current_hay, substring, score_cutoff=FUZZY_APROXIMATION_MIN_SCORE
        )
        if first_alignment is None:
            # TODO: Fail if no initial alignment
            return

        # TODO: Extend with range
        smaller_hay = _get_smaller_hay_around_alignment(current_hay, first_alignment)
        max_sim_string = refine_match(smaller_hay, substring)
        if not max_sim_string:
            # TODO: Fail if not max_sim_string
            return
        # Rematch to find the index with the string extracted from current hay
        alignment = fuzz.partial_ratio_alignment(
            current_hay, max_sim_string, score_cutoff=FUZZY_MATCH_MIN_SCORE
        )
        if alignment is not None:
            yield Range(
                start_pos=current_start + alignment.src_start,
                end_pos=current_start + alignment.src_end,
            )
            current_start += alignment.src_end
            current_hay = long_string[current_start:]


def _get_smaller_hay_around_alignment(current_hay: str, first_alignment):
    extended_range = extend_substring_range(
        complete_string_len=len(current_hay),
        substring_range=Range(first_alignment.src_start, first_alignment.src_end),
        extension_length=int(
            0.2 * (first_alignment.src_end - first_alignment.src_start) + 10
        ),
    )
    smaller_hay = current_hay[extended_range.start_pos : extended_range.end_pos]

    return smaller_hay


def refine_match(current_hay, substring):
    needle_length = len(substring.split())
    max_sim_val = 0
    max_sim_string = ""
    hay_tokens = tokenize_from_text(current_hay)

    # Todo consider less grams length
    for ngram in ngrams(hay_tokens, min(needle_length, len(hay_tokens))):
        hay_ngram = untokenize_to_text(ngram)
        similarity = SM(None, hay_ngram, substring).ratio()
        if similarity > max_sim_val and similarity > FUZZY_MATCH_MIN_SCORE / 100.0:
            max_sim_val = similarity
            max_sim_string = hay_ngram
    return max_sim_string
