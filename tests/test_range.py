from highlights_prettifier.range import (
    Range,
    calculate_overlap,
    extend_substring_range,
)


def test_no_overlap():
    range1 = Range(0, 5)
    range2 = Range(10, 15)
    overlap = calculate_overlap(range1, range2)
    assert overlap is None


def test_partial_overlap():
    range1 = Range(5, 15)
    range2 = Range(10, 20)
    overlap = calculate_overlap(range1, range2)
    assert overlap == Range(10, 15)


def test_full_overlap():
    range1 = Range(5, 15)
    range2 = Range(0, 20)
    overlap = calculate_overlap(range1, range2)
    assert overlap == Range(5, 15)


def test_same_range():
    range1 = Range(5, 15)
    range2 = Range(5, 15)
    overlap = calculate_overlap(range1, range2)
    assert overlap == Range(5, 15)


def test_extend_substring_within_bounds():
    complete_string_len = 20
    substring_range = Range(12, 15)
    extended_range = extend_substring_range(
        complete_string_len, substring_range, extension_length=5
    )

    assert extended_range == Range(
        7, 20
    )  # Expected extended range within bounds


def test_extend_substring_to_boundary():
    complete_string_len = 44
    substring_range = Range(5, 30)  # Already at the boundary
    extended_range = extend_substring_range(
        complete_string_len, substring_range, extension_length=10
    )

    assert extended_range == Range(0, 40)  #
