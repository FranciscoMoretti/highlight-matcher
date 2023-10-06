from shlex import join
from typing import List
from highlights_prettifier.range import Range
from rapidfuzz import fuzz


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
    return " ", join(tokens)


def fuzzy_find_substrings_sequence(long_string: str, substrings: List[str]):
    tokens = tokenize(long_string)
    substrings_tokens = [tokenize(substring) for substring in substrings]

    substrings_index = 0
    current_start = 0

    for substring in substrings:
        alignment = fuzz.partial_ratio_alignment(long_string, substring)
        if alignment is not None:
            start_pos = alignment.src_start
            while long_string[start_pos] == " ":
                start_pos += 1
            end_pos = alignment.src_end
            while long_string[end_pos - 1] == " ":
                end_pos -= 1
            yield Range(start_pos=start_pos, end_pos=end_pos)
        # TODO: else: ERROR?

    # while substrings_index < len(substrings_tokens):
    #     current_substring_tokens = substrings_tokens[substrings_index]

    #     for i in range(current_start, len(tokens) - len(current_substring_tokens) + 1):
    #         sub_tokens = tokens[i : i + len(current_substring_tokens)]
    #         match_ratio = normalized_ratio(
    #             untokenize(current_substring_tokens), untokenize(sub_tokens)
    #         )

    #         if match_ratio >= FUZZY_MATCH_MIN_SCORE:
    #             yield Range(i, i + len(current_substring_tokens) - 1)
    #             current_start = i + len(current_substring_tokens)
    #             break

    #     substrings_index += 1
