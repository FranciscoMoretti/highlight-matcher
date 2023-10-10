import pytest

from highlights_prettifier.format_highlights import create_formated_highlights

article_content_0 = "In Topic 8, [​*The Essence of Good Design*​](#f_0026.xhtml#essence_of_design) we claim that using good design principles will make the code you write easy to change. Coupling is the enemy of change, because it links together things that must change in parallel. This makes change more difficult: either you spend time tracking down all the parts that need changing, or you spend time wondering why things broke when you changed “just one thing” and not the other things to which it was coupled. "
highlights_0 = [
    "Coupling is the enemy of change, because it links together things that must change in parallel. This makes change more difficult: either you spend time tracking down all the parts that need changing, or you spend time wondering why things broke when you changed “just one thing” and not the other things to which it was coupled.",
]
expected_formatted_highlights_0 = "<p>Coupling is the enemy of change, because it links together things that must change in parallel. This makes change more difficult: either you spend time tracking down all the parts that need changing, or you spend time wondering why things broke when you changed “just one thing” and not the other things to which it was coupled.</p>\n"


@pytest.mark.parametrize(
    "article_text, highlights, expected_formatted_highlights",
    [
        (
            article_content_0,
            highlights_0,
            expected_formatted_highlights_0,
        ),
    ],
)
def test_create_formated_highlights(
    article_text, highlights, expected_formatted_highlights
):
    formatted_highlights = create_formated_highlights(article_text, highlights)
    assert formatted_highlights == expected_formatted_highlights


# Make sure to replace the functions with their actual implementations.
