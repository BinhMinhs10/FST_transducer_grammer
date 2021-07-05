"""Simple implementation t9 of a T9 processor

for a given t9 input it return a lattice of decoded phrases
"""

from typing import Iterable
import pynini
from pynini.lib import pynutil
from pynini.lib import rewrite


class T9:
    """Simple implementation of a  T9 processor"""

    _t9_map = [
        ("0", [" "]),
        ("2", ["a", "b", "c"]),
        ("3", ["d", "e", "f"]),
        ("4", ["g", "h", "i"]),
        ("5", ["j", "k", "l"]),
        ("6", ["m", "n", "o"]),
        ("7", ["p", "q", "r", "s"]),
        ("8", ["t", "u", "v"]),
        ("9", ["w", "x", "y", "z"]),
    ]

    def __init__(self, lexicon: Iterable[str]):
        self._make_fst()
        self._make_lexicon(lexicon)

    def _make_fst(self) -> None:
        self._decoder = pynini.Fst()
        for (inp, outs) in self._t9_map:
            self._decoder |= pynini.cross(inp, pynini.union(*outs))
        self._decoder.closure().optimize()
        self._encoder = pynini.invert(self._decoder)

    def _make_lexicon(self, lexicon: Iterable[str]) -> None:
        lexicon_fst = pynini.string_map(lexicon)
        self._lexicon = pynutil.join(lexicon_fst, " ").optimize()

    def decode(self, t9_input: pynini.FstLike) -> pynini.Fst:
        lattice = rewrite.rewrite_lattice(t9_input, self._decoder)
        return pynini.intersect(lattice, self._lexicon)

    def encode(self, text: pynini.FstLike) -> str:
        return rewrite.top_rewrite(text, self._encoder)


if __name__ == "__main__":
    lexicon = [
        "the",
        "cool",
        "warthog",
        "escaped",
        "easily",
        "from",
        "baltimore",
        "zoo",
        "col",
    ]
    example = "the cool warthog escaped easily from baltimore zoo"
    t9 = T9(lexicon)
    encoded = t9.encode(example)
    print(encoded)
    decode = t9.decode(encoded).paths().ostring()
    print(decode)
