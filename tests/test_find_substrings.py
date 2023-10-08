import pytest
from highlights_prettifier.range import substring_with_range
from highlights_prettifier.highlight_finder import (
    find_substrings_sequence,
    fuzzy_find_substrings_sequence,
    refine_matching_sequences,
    refine_matching_tokens,
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
    substrings = ["example  of  fuzzy", "matching- in"]
    result_ranges = list(fuzzy_find_substrings_sequence(long_string, substrings))
    result_string = [
        substring_with_range(long_string, range) for range in result_ranges
    ]
    expected = ["example of fuzzy", "matching in"]
    assert result_string == expected


# TODO: Fix unit test
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


@pytest.mark.parametrize(
    "hay, needle, expected",
    [
        (
            "title} Life doesn't stand still. Neither can the code that we write. In order to keep up with today's near-frantic pace of change, we need to make every effort to write code that's as loose---as flexible---as possible. Otherwise we may find our code quickly becoming outdated, or too brittle to fix, and may ultimately be left behind in the mad dash toward the future. Back in ",
            "Life doesn’t stand still. Neither can the code that we write. In order to keep up with today’s near-frantic pace of change, we need to make every effort to write code that’s as loose—as flexible—as possible. Otherwise we may find our code quickly becoming outdated, or too brittle to fix, and may ultimately be left behind in the mad dash toward the future.",
            "Life doesn't stand still. Neither can the code that we write. In order to keep up with today's near-frantic pace of change, we need to make every effort to write code that's as loose---as flexible---as possible. Otherwise we may find our code quickly becoming outdated, or too brittle to fix, and may ultimately be left behind in the mad dash toward the future.",
        ),
        (
            " This means there's a simple principle you should follow: Tip 44   Decoupled Code Is Easier to Change Given that we don't normally code using steel beams and rivets, just what does it mean to decouple code? In this section we'll talk about: Train wrecks---chains of method calls Globalization---the dangers of static things Inheritance---why subclassing is dangerous To some extent this list is artificial: coupling can occur just about any time two pieces of code share something, so as you read what follows keep an eye out for the underlying patterns so you can apply them to [your]{.emph} code. And keep a lookout for some of the symptoms of coupling: Wacky dependencies between unrelated modules or libraries. \"Simple\" changes to one module that propagate through unrelated modules in the system or break stuff elsewhere in the system. Developers who are afraid to change code because they aren't sure what might be affected. Meetings where everyone has to attend because no one is sure who will be affected by a change. Train Wrecks We've all seen (and probably written) code like this: \u200b[\xa0]{.codeprefix}   \u200b public \u200b \u200b void \u200b applyDiscount(customer, order_id, discount) { \u200b[\xa0]{.codeprefix}   totals = customer \u200b[",
            "Tip 44 Decoupled Code Is Easier to Change Given that we don’t normally code using steel beams and rivets, just what does it mean to decouple code? In this section we’ll talk about: Train wrecks—chains of method calls Globalization—the dangers of static things Inheritance—why subclassing is dangerous To some extent this list is artificial: coupling can occur just about any time two pieces of code share something, so as you read what follows keep an eye out for the underlying patterns so you can apply them to your code. And keep a lookout for some of the symptoms of coupling: Wacky dependencies between unrelated modules or libraries. “Simple” changes to one module that propagate through unrelated modules in the system or break stuff elsewhere in the system. Developers who are afraid to change code because they aren’t sure what might be affected. Meetings where everyone has to attend because no one is sure who will be affected by a change.",
            "Tip 44 Decoupled Code Is Easier to Change Given that we don't normally code using steel beams and rivets, just what does it mean to decouple code? In this section we'll talk about: Train wrecks---chains of method calls Globalization---the dangers of static things Inheritance---why subclassing is dangerous To some extent this list is artificial: coupling can occur just about any time two pieces of code share something, so as you read what follows keep an eye out for the underlying patterns so you can apply them to [your]{.emph} code. And keep a lookout for some of the symptoms of coupling: Wacky dependencies between unrelated modules or libraries. \"Simple\" changes to one module that propagate through unrelated modules in the system or break stuff elsewhere in the system. Developers who are afraid to change code because they aren't sure what might be affected. Meetings where everyone has to attend because no one is sure who will be affected by a change.",
        )
        # Add more test cases as needed
    ],
)
def test_refine_match_matching_tokens(hay, needle, expected):
    result = refine_matching_tokens(hay, needle)
    assert result == expected


@pytest.mark.parametrize(
    "hay, needle, expected",
    [
        (
            " We discuss [Tell, Don't Ask]{.emph} in o",
            "Tell, Don’t Ask",
            "Tell, Don't Ask",
        ),
        (
            " We discuss [Tell, Don't Ask]{.emph} in o",
            "We discuss Tell, Don't Ask in",
            "We discuss [Tell, Don't Ask]{.emph} in",
        ),
        (
            "We We We discuss [Tell, Don't Ask]{.emph} in o o o",
            "We discuss Tell, Don't Ask in",
            "We discuss [Tell, Don't Ask]{.emph} in",
        )
        # Add more test cases as needed
    ],
)
def test_refine_match_adjusting_length(hay, needle, expected):
    result = refine_matching_sequences(hay, needle)  # TODO: Change func
    assert result == expected
