import pynini
from pynini.lib import pynutil
from pynini.lib import rewrite


def _priority_union(q: pynini.Fst, r: pynini.Fst, sigma: pynini.Fst) -> pynini.Fst:
    complement_domain_q = sigma - pynini.project(q, "input")
    return pynini.union(q, complement_domain_q @ r)


# the inventor
_v = pynini.union("a", "e", "i", "o", "u")
_c = pynini.union(
    "b",
    "c",
    "d",
    "f",
    "g",
    "h",
    "j",
    "k",
    "l",
    "m",
    "n",
    "p",
    "q",
    "r",
    "s",
    "t",
    "v",
    "w",
    "x",
    "y",
    "z",
)
_sigma = pynini.union(_v, _c).closure().optimize()

_suppletive = pynini.string_map(
    [
        "deer",
        "fish",
        "sheep",
        # Stem changes.
        ("foot", "feet"),
        ("goose", "geese"),
        ("man", "men"),
        ("mouse", "mice"),
        ("tooth", "teeth"),
        ("woman", "women"),
        # Irregular suffixes
        ("child", "children"),
        ("ox", "oxen"),
        # f -> v
        ("wife", "wives"),
        ("wolf", "wolves"),
        # a few Greek and latin plurals
        ("analysis", "analyses"),
        ("criterion", "criteria"),
        ("focus", "foci"),
    ]
)
_ies = _sigma + _c + pynini.cross("y", "ies")
_es = _sigma + pynini.union("s", "sh", "ch", "x", "z") + pynutil.insert("es")
_s = _sigma + pynutil.insert("s")

# priority union
_plural = _priority_union(
    _suppletive, _priority_union(_ies, _priority_union(_es, _s, _sigma), _sigma), _sigma
).optimize()


def plural(singular: str) -> str:
    return rewrite.one_top_rewrite(singular, _plural)


if __name__ == "__main__":
    for singular in ["analysis", "boy", "deer", "hamlet", "house", "wife", "puppy"]:
        print(plural(singular))
