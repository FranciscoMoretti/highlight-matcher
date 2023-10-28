from unidecode import unidecode
import re


def default_preprocess(seq):
    """
    normalized_1:
        Convert all characters to lower case
    normalized_2:
        Remove multiple whitespace characters (space, tab, newline, return, formfeed)
    normalized_2:
        Single whitespace chars are space
    unicode:
        convert unicode to ascii
    TODO: removing all non alphanumeric characters ?
    TODO: trimming whitespaces ?
    """
    normalized_1 = str(seq).lower()
    normalized_2 = re.sub("\s{2,}", " ", normalized_1)
    normalized_3 = re.sub("\s", " ", normalized_2)
    return unidecode(normalized_3)
