from rapidfuzz import fuzz, process


from nltk.util import everygrams

from highlights_prettifier.default_tuning import FUZZY_MATCH_MIN_SCORE

from highlights_prettifier.preprocess import default_preprocess


def tokenize_from_text(text):
    # Tokenize the input string into words (tokens)
    # TODO: This operation is not safe for multiple whitespaces because it doesn't count
    # them and then it joins them with a single whitespace
    return text.split()


def untokenize_to_text(tokens):
    return " ".join(tokens)


def refine_matching(hay, needle):
    needle_tokens = tokenize_from_text(needle)
    hay_tokens = tokenize_from_text(hay)
    max_sim_string = ""

    # TODO: Improve it by using relative bloats
    hay_candidates = [
        untokenize_to_text(ngram)
        for ngram in everygrams(
            hay_tokens,
            min_len=min(len(needle_tokens) - 2, len(hay_tokens)),
            max_len=max(len(needle_tokens) + 5, len(hay_tokens)),
        )
    ]

    best_match = process.extractOne(
        needle,
        hay_candidates,
        scorer=fuzz.ratio,
        processor=default_preprocess,
        score_hint=98,
    )

    if best_match:
        match_string, match_score, _ = best_match
        if match_score < 100:
            if not needle.endswith("..."):
                print(f"Score {match_score}")
        if match_score > FUZZY_MATCH_MIN_SCORE:
            max_sim_string = match_string
    if not max_sim_string:
        best_matches = process.extract(
            needle, hay_candidates, scorer=fuzz.ratio, limit=3
        )
        print(f"Couldn't match the following {[hay, needle]}")
        print(f"Best matches: {best_matches}")
    return max_sim_string
