"""Grammar to ham

consider the following cases
for simplicity assume that all text is case-free (lower case)
"""
import string
import pynini
from typing import List
from pynini.lib import byte, pynutil, rewrite


# TODO: more than 1 token
def _plus(token: pynini.FstLike) -> pynini.Fst:
    return pynini.closure(token, 1)


# TODO: zero or more token
def _star(token: pynini.FstLike) -> pynini.Fst:
    return pynini.closure(token)


# TODO: 1 token
def _ques(token: pynini.FstLike) -> pynini.Fst:
    return pynini.closure(token, 0, 1)


_sigma_star = pynini.closure(byte.BYTE).optimize()


# TODO: normalization engiens
#  (deduplicator, regular expressions, abb expander, a lexicon)
class Deduplicator:
    """container for a deduplicator for all letters."""

    _dedup: pynini.FstLike
    _lexicon: pynini.FstLike

    def __init__(self, lexicon: pynini.Fst):
        """Constructs the deduplicator.

        Args:
            lexicon: an FSA representiong the lexicon
        """
        it = iter(string.ascii_lowercase)
        letter = next(it)
        self._dedup = Deduplicator.dedup_rule(letter)
        for letter in it:
            self._dedup @= Deduplicator.dedup_rule(letter)
            self._dedup.optimize()
        self._lexicon = lexicon

    @staticmethod
    def dedup_rule(letter: str) -> pynini.Fst:
        """compiles transducer that optionally deletes multiple letters

        Args:
            letter: a letter
        """
        not_letter = byte.LOWER - letter
        return pynini.cdrewrite(
            pynini.cross(_plus(letter), _ques(letter)),
            ("[BOS]" | not_letter) + letter,
            ("[EOS]" | not_letter),
            _sigma_star,
        )

    def expand(self, token: pynini.FstLike) -> pynini.Fst:
        """Find deduplicate candidates for a token in a lexicon

        Args:
            token: a "cooool" like token
        Returns:
            an FST representing a lattice of possible matches.
        """
        try:
            lattice = rewrite.rewrite_lattice(token, self._dedup)
            return rewrite.rewrite_lattice(lattice, self._lexicon)
        except rewrite.Error:
            return pynini.Fst()

    def expand_string(self, s: str) -> List[str]:
        return rewrite.lattice_to_strings(self.expand(s))


class Deabbreviator:
    """Expands abbreviations formed by deleting vowels or sonorants

    the result must
    """

    pass


class Lexicon:
    """container for a substitution lexicon."""

    _lexicon: pynini.Fst

    def __init__(self, path: str):
        self._lexicon = pynini.string_file(path).optimize()

    def expand(self, token: pynini.FstLike) -> pynini.Fst:
        try:
            return rewrite.rewrite_lattice(token, self._lexicon)
        except rewrite.Error:
            return pynini.Fst()


class Regexps:
    """container for regexp substitutions"""

    _regexps = pynini.union(
        pynini.cross("b" + _plus("b") + _star("z"), "bye bye"),
        pynini.cross("congrat" + _star("z"), "congratulations"),
        pynini.cross("cool" + _plus("z"), "cool"),
        pynini.cross("delis" + _plus("h"), "delicious"),
        pynini.cross("e" + _plus("r"), "uh"),  # Forcing newline.
        pynini.cross("f" + _plus("f"), "ff"),
        pynini.cross("g" + _plus("l"), "good luck"),
        pynini.cross("he" + _plus("y") + "z", "hey"),
        pynini.cross("he" + _ques("'") + _plus("z"), "he's"),
        pynini.cross("how" + _ques("'") + _plus("z"), "how is"),
        pynini.cross("how" + _ques("'") + _plus("z"), "how has"),
        pynini.cross("how" + _ques("'") + _plus("z"), "how was"),
        pynini.cross("how" + _ques("'") + _plus("z"), "how does"),
        pynini.cross("kew" + _plus("l") + _star("z"), "cool"),
        pynini.cross("k" + _plus("k"), "ok"),
        pynini.cross("ko" + _plus("o") + "l", "cool"),
        pynini.cross("k" + _plus("z"), "ok"),
        pynini.cross(
            _plus("l") + pynini.union("o", "u").closure(1) + _plus("l") + _plus("z"),
            pynini.union("laugh out loud", "laugh"),
        ),
        pynini.cross(_plus("l") + _plus("u") + _plus("r") + _plus("v"), "love"),
        pynini.cross(
            _plus("l") + _plus("u") + _plus("v") + _plus("e") + _plus("e"), "love"
        ),
        pynini.cross("mis" + _plus("h"), "miss"),
        pynini.cross("m" + _plus("m") + "k", "mm ok"),
        pynini.cross("n00b" + _plus("z"), "newbie"),
        pynini.cross("na" + _plus("h"), "no"),
        pynini.cross("no" + _plus("e") + _plus("z"), "no"),
        pynini.cross("noob" + _plus("z"), "newbie"),
        pynini.cross("oke" + _plus("e"), "okay"),
        pynini.cross("oki" + _plus("e"), "okay"),
        pynini.cross("ok" + _plus("z"), "okay"),
        pynini.cross("om" + _plus("g"), "oh my god"),
        pynini.cross("omg" + _plus("z"), "oh my god"),
        pynini.cross("orly" + _plus("z"), "oh really"),
        pynini.cross("pl" + _plus("z"), "please"),
        pynini.cross("pw" + _plus("e") + "ase", "please"),
        pynini.cross("q" + _plus("n"), "_question"),
        pynini.cross("qool" + _plus("z"), "cool"),
        pynini.cross("rox0r" + _plus("z"), "rocks"),
        pynini.cross("sorry" + _plus("z"), "sorry"),
        pynini.cross("s" + _plus("o") + "w" + _plus("w") + _plus("y"), "sorry"),
        pynini.cross("sry" + _plus("z"), "sorry"),
        pynini.cross("thanke" + _plus("w"), "thank you"),
        pynini.cross("thank" + _plus("q"), "thank you"),
        pynini.cross("t" + _plus("q"), "thank you"),
        pynini.cross("t" + _plus("y"), "thank you"),
        pynini.cross("tyv" + _plus("m"), "thank you very much"),
        pynini.cross(_plus("u"), "you"),  # Forcing newline.
        pynini.cross("ug" + _plus("h"), "ugh"),
        pynini.cross("u" + _plus("h"), "uh"),
        pynini.cross("wai" + _plus("t"), "wait"),
        pynini.cross("w" + _plus("a") + _plus("z"), "what's"),
        pynini.cross("w" + _plus("a") + _plus("z") + _plus("a"), "what's up"),
        pynini.cross(_plus("wa") + _plus("z") + _plus("u") + _plus("p"), "what's up"),
        pynini.cross("wh" + _plus("a"), "what"),
        pynini.cross("w" + _plus("u") + _plus("t"), "what"),
        pynini.cross(_plus("xo"), "'hugs and kisses'"),
        pynini.cross("ya" + _plus("h"), "yeah"),
        pynini.cross("ya" + _plus("r"), "yeah"),
        pynini.cross("ye" + _plus("a"), "yeah"),
        pynini.cross("yes" + _plus("h"), "yes"),
        pynini.cross("ye" + _plus("z"), "yes"),
        pynini.cross("yup" + _plus("s"), "yup"),
        pynini.cross("yup" + _plus("z"), "yup"),
        pynini.cross("zom" + _plus("g"), "oh my god"),
        pynini.cross("z" + _plus("u") + _plus("p"), "what's up"),
    ).optimize()

    def expand(self, token: pynini.FstLike) -> pynini.Fst:
        """Find regexps candidates for a token

        Args:
            token: a "zomggg"

        Returns:
            An FST representing a lattice of possible matches
        """
        try:
            return rewrite.rewrite_lattice(token, self._regexps)
        except rewrite.Error:
            return pynini.Fst()

    def expand_string(self, s: str) -> List[str]:
        return rewrite.lattice_to_strings(self.expand(s))


if __name__ == "__main__":
    lexicon = pynini.union(
        "the", "cool", "warthog", "escaped", "essily", "from", "baltimore", "zoo", "col"
    )
    deduplicator = Deduplicator(lexicon)
    result = deduplicator.expand_string("coooool")
    print(result)

    regexps = Regexps()
    result = regexps.expand_string("zomggggggg")
    print(result)
    result = regexps.expand_string("he'z")
    print(result)
