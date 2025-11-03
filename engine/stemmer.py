"""
Implement a rudimentary porter stemmer.

Let's remove common prefixes and suffixes from English words.
"""


def stem(word: str) -> str:
    """
    Rules:
      remove prefixes and suffixes only if :
      (i) word is longer than affix
      AND
      (ii) post-removal token is at least of length 3.
    """
    prefixes = [
        "un",
        "re",
        "in",
        "im",
        "dis",
        "en",
        "non",
        "over",
        "mis",
        "sub",
        "pre",
        "inter",
        "fore",
        "de",
        "trans",
        "super",
        "semi",
        "anti",
        "mid",
        "under",
    ]
    suffixes = [
        "ing",
        "ed",
        "ly",
        "es",
        "s",
        "ment",
        "ness",
        "ful",
        "less",
        "ation",
        "tion",
        "ity",
        "al",
        "er",
        "or",
        "ive",
        "ize",
        "ise",
        "y",
    ]

    # Remove prefixes
    for prefix in prefixes:
        if word.startswith(prefix) and len(word) > len(prefix) + 2:
            word = word[len(prefix) :]
            break
    # Remove suffixes
    for suffix in suffixes:
        if word.endswith(suffix) and len(word) > len(suffix) + 2:
            word = word[: -len(suffix)]
            break
    return word
