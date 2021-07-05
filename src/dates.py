"""Grammar for extracting possible dates from running tests"""

import string
import pynini
from pynini.lib import byte, pynutil, rewrite


def _possibly_zero_padded(top: int):
    """Adds optional leading '0' to single-digit numbers in a range

    Args:
        top: top of the range
    Returns:
        an FST representing number from 1 to top inclusive
    """
    nums = [str(d) for d in range(1, top + 1)]
    nums = [f"{d:02d}" for d in range(1, top + 1)] + nums
    return pynini.union(*nums).optimize()


_lowercase = pynini.union(
    *[pynini.cross(x.upper(), x) for x in string.ascii_lowercase]
).closure()
_sigma_star = pynini.closure(byte.BYTE)
_tolower = pynini.cdrewrite(_lowercase, "", "", _sigma_star)

_month_map = [
    ["1", ["january", "jan", "jan."]],
    ["2", ["february", "feb", "feb."]],
    ["3", ["march", "mar", "mar."]],
    ["4", ["april", "apr", "apr."]],
    ["5", ["may"]],
    ["6", ["june", "jun", "jun."]],
    ["7", ["july", "jul", "jul."]],
    ["8", ["august", "aug", "aug."]],
    ["9", ["september", "sept", "sept", "sep", "sep."]],
    ["10", ["october", "oct", "oct."]],
    ["11", ["november", "nov", "nov."]],
    ["12", ["december", "dec", "dec."]],
]

# *x[1] define list
_month_names = pynini.union(
    *(pynini.cross(pynini.union(*x[1]), x[0]) for x in _month_map)
).optimize()
_month_nums = pynini.union(*(m[0] for m in _month_map)).optimize()

_space = pynini.accep(" ") ** (1, ...)

# TODO(rws): make these match for months
_day_nums = _possibly_zero_padded(31)

_four_etc = pynini.union("4", "5", "6", "7", "8", "9", "0")

_day_ordinal = (
    (_day_nums @ (_sigma_star + "1")) + pynutil.delete("st")
    | (_day_nums @ (_sigma_star + "2")) + pynutil.delete("nd")
    | (_day_nums @ (_sigma_star + "3")) + pynutil.delete("rd")
    | (_day_nums @ (_sigma_star + _four_etc)) + pynutil.delete("th").optimize()
)

_digit = [str(d) for d in range(10)]
_digit_no_zero = [str(d) for d in range(1, 10)]

# negative weight on year favors picking a longer include a year rather than just month and day, if a possible year is present.
_year = pynutil.add_weight(
    pynini.union(*_digit_no_zero) + pynini.union(*_digit) ** 3, -1
).optimize()


def _markup(expr: pynini.FstLike, mark: str) -> pynini.Fst:
    """Introduces XML markup

    Args:
        expr: an FST
        mark: the name to apply to the region
    Returns:
        An FST mapping from expr to <mark>expr</mark>
    """
    markup = pynutil.insert(f"<{mark}>")
    markup.concat(expr)
    markup.concat(pynutil.insert(f"</{mark}>"))
    return markup.optimize()


_mdy_full_date = (
    _markup(_month_names, "month")
    + pynutil.delete(_space)
    + _markup(_day_nums, "day")
    + (pynutil.delete(",").ques + pynutil.delete(_space) + _markup(_year, "year")).ques
)

_mdy_full_date_ordinal = (
    _markup(_month_names, "month")
    + pynutil.delete(_space)
    + pynutil.delete("the" + _space)
    + _markup(_day_nums, "day")
    + (pynutil.delete(",").ques + pynutil.delete(_space) + _markup(_year, "year")).ques
)

_dmy_full_date = (
    _markup(_month_names, "day")
    + pynutil.delete(_space)
    + _markup(_day_nums, "month")
    + (pynutil.delete(",").ques + pynutil.delete(_space) + _markup(_year, "year")).ques
)

_dmy_full_date_ordinal = (
    pynutil.delete("the" + _space)
    + _markup(_month_names, "day")
    + pynutil.delete(_space)
    + pynutil.delete("of" + _space)
    + _markup(_day_nums, "month")
    + (pynutil.delete(",").ques + pynutil.delete(_space) + _markup(_year, "year")).ques
)

_numeric_ymd = (
    _markup(_year, "year")
    + pynutil.delete("/")
    + _markup(_month_names, "month")
    + pynutil.delete("/")
    + _markup(_day_nums, "day")
    + _markup(_year, "year")
)

_numeric_dmy = (
    _markup(_day_nums, "day")
    + pynutil.delete("/")
    + _markup(_month_nums, "month")
    + pynutil.delete("/")
    + _markup(_year, "year")
)

_month_year = (
    _markup(_month_names, "month") + pynutil.delete(_space) + _markup(_year, "year")
)
_date = (
    _mdy_full_date
    | _mdy_full_date_ordinal
    | _dmy_full_date
    | _dmy_full_date_ordinal
    | _numeric_ymd
    | _numeric_dmy
    | _month_year
)
# And wrap the whole thing with <date>.
_date = _markup(_date, "date")

# TODO: FST @ FST to continue FST
_date_matcher = (_tolower @ _date).optimize()

_date_tagger = pynini.cdrewrite(_date_matcher, "", "", _sigma_star).optimize()


def match(text: str) -> str:
    return rewrite.one_top_rewrite(text, _date_matcher)


def tag(text: str) -> str:
    # return rewrite.one_top_rewrite(text, _date_tagger)
    return pynini.shortestpath(pynini.compose(text, _date_tagger)).string()


if __name__ == "__main__":
    print(match("2/1/1985"))

    text = """I met John on June 1, 1985 in Colorado."""
    result = tag(text)
    print(result)
