from typing import List
from highlights_prettifier.range import Range
from rapidfuzz import fuzz
from difflib import SequenceMatcher as SM
from nltk.util import ngrams

FUZZY_MATCH_MIN_SCORE = 90


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


def tokenize(text):
    # Tokenize the input string into words (tokens)
    # TODO: This operation is not safe for multiple whitespaces because it doesn't count
    # them and then it joins them with a single whitespace
    return text.split()


def untokenize(tokens):
    return " ".join(tokens)


# Algorithm find in https://stackoverflow.com/questions/17740833/checking-fuzzy-approximate-substring-existing-in-a-longer-string-in-python
# Other alternatives in same question
def fuzzy_find_substrings_sequence(long_string: str, substrings: List[str]):
    current_start = 0
    current_hay = long_string

    for substring in substrings:
        needle_length = len(substring.split())
        max_sim_val = 0
        max_sim_string = ""

        for ngram in ngrams(
            tokenize(current_hay), needle_length + int(0.2 * needle_length)
        ):
            hay_ngram = untokenize(ngram)
            similarity = SM(None, hay_ngram, substring).ratio()
            if similarity > max_sim_val and similarity > FUZZY_MATCH_MIN_SCORE / 100.0:
                max_sim_val = similarity
                max_sim_string = hay_ngram
        if max_sim_string:
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
