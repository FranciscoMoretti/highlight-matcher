from highlights_prettifier.range import Range, calculate_overlap


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
