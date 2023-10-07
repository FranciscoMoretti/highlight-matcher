from highlights_prettifier.range import Range, substring_with_range
from highlights_prettifier.highlight_finder import (
    find_substrings_sequence,
    fuzzy_find_substrings_sequence,
    refine_match,
    tokenize_from_text,
)


def test_find_substring_positions():
    long_string = "This is a long string with some substrings."
    substrings = ["long", "with", "substrings"]
    positions = list(find_substrings_sequence(long_string, substrings))

    assert substrings == [
        long_string[positions[0].start_pos : positions[0].end_pos],
        long_string[positions[1].start_pos : positions[1].end_pos],
        long_string[positions[2].start_pos : positions[2].end_pos],
    ]


def test_no_match():
    long_string = "This is a long string with some substrings."
    substrings = ["not", "found"]
    positions = list(find_substrings_sequence(long_string, substrings))

    assert positions == []


def test_fuzzy_find_exact_match():
    long_string = "This is an example of fuzzy matching in Python."
    substrings = ["example  of", "fuzzy matching  in  Python."]
    result_ranges = list(fuzzy_find_substrings_sequence(long_string, substrings))
    result_string = [
        substring_with_range(long_string, range) for range in result_ranges
    ]
    expected = ["example of", "fuzzy matching in Python."]
    assert result_string == expected


def test_fuzzy_find_partial_match():
    long_string = "This is an example of fuzzy matching in Python."
    substrings = ["example  of  fuzzy ", "matching- in"]
    result_ranges = list(fuzzy_find_substrings_sequence(long_string, substrings))
    result_string = [
        substring_with_range(long_string, range) for range in result_ranges
    ]
    expected = ["example of fuzzy", "matching in"]
    assert result_string == expected


def test_fuzzy_find_no_match():
    long_string = "This is an example of fuzzy matching in Python."
    substrings = ["nonexistent   substring", "not   found"]
    result = list(fuzzy_find_substrings_sequence(long_string, substrings))
    expected = []
    assert result == expected


def test_tokenization():
    format_1 = "Life doesn't stand still. Neither can the code that we write. In order to keep up with today's near-frantic pace of change, we need to make every effort to write code that's as loose---as flexible---as possible. Otherwise we may find our code quickly becoming outdated, or too brittle to fix, and may ultimately be left behind in the mad dash toward the future."
    format_2 = "Life doesn’t stand still. Neither can the code that we write. In order to keep up with today’s near-frantic pace of change, we need to make every effort to write code that’s as loose—as flexible—as possible. Otherwise we may find our code quickly becoming outdated, or too brittle to fix, and may ultimately be left behind in the mad dash toward the future."
    tokens_1 = tokenize_from_text(format_1)
    tokens_2 = tokenize_from_text(format_2)
    assert len(tokens_1) == len(tokens_2)


def test_refine_match():
    hay = "title} Life doesn't stand still. Neither can the code that we write. In order to keep up with today's near-frantic pace of change, we need to make every effort to write code that's as loose---as flexible---as possible. Otherwise we may find our code quickly becoming outdated, or too brittle to fix, and may ultimately be left behind in the mad dash toward the future. Back in "
    needle = "Life doesn’t stand still. Neither can the code that we write. In order to keep up with today’s near-frantic pace of change, we need to make every effort to write code that’s as loose—as flexible—as possible. Otherwise we may find our code quickly becoming outdated, or too brittle to fix, and may ultimately be left behind in the mad dash toward the future."
    result = refine_match(hay, needle)
    expected = "Life doesn't stand still. Neither can the code that we write. In order to keep up with today's near-frantic pace of change, we need to make every effort to write code that's as loose---as flexible---as possible. Otherwise we may find our code quickly becoming outdated, or too brittle to fix, and may ultimately be left behind in the mad dash toward the future."
    assert result == expected
