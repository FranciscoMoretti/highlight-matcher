from ..highlights_prettifier.highlight_finder import find_substrings_sequence


def test_find_substring_positions():
    long_string = "This is a long string with some substrings."
    substrings = ["long", "with", "substrings"]
    positions = list(find_substrings_sequence(long_string, substrings))

    assert substrings == [
        long_string[positions[0][0] : positions[0][1]],
        long_string[positions[1][0] : positions[1][1]],
        long_string[positions[2][0] : positions[2][1]],
    ]


def test_no_match():
    long_string = "This is a long string with some substrings."
    substrings = ["not", "found"]
    positions = list(find_substrings_sequence(long_string, substrings))

    assert positions == []
