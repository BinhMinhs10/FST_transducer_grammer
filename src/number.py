"""Simple number name grammar for English, to 10 million"""

import string
import pynini
from pynini.lib import pynutil, rewrite

# Inventories
# print(*string.digits)
# 0, 1, 2 ..., 9
_digit = pynini.union(*string.digits)

# special symbol we will use the teens below
_powers = pynini.union("[E1]", "[E1*]", "[E2]", "[E3]", "[E6]")
_sigma_star = pynini.union(_digit, _powers).closure().optimize()

_raw_factorizer = (
    _digit
    + pynutil.insert("[E6]")
    + _digit
    + pynutil.insert("[E2]")
    + _digit
    + pynutil.insert("[E1]")
    + _digit
    + pynutil.insert("[E3]")
    + _digit
    + pynutil.insert("[E2]")
    + _digit
    + pynutil.insert("[E1]")
    + _digit
)

_del_zeros = (
    pynini.cdrewrite(pynutil.delete("0"), "", "[EOS]", _sigma_star)
    @ pynini.cdrewrite(pynutil.delete("0[E1]"), "", "", _sigma_star)
    @ pynini.cdrewrite(pynutil.delete("0[E2]"), "", "", _sigma_star)
    @ pynini.cdrewrite(pynutil.delete("0[E3]"), "[E6]", "", _sigma_star)
    @ pynini.cdrewrite(pynutil.delete("0[E6]"), "", "", _sigma_star)
    @ pynini.cdrewrite(pynutil.delete("0"), "", "", _sigma_star)
).optimize()

_pad_zeros = pynutil.insert("0").closure().concat(pynini.closure(_digit))

# changes E1 to E1* for 11-19
_fix_teens = pynini.cdrewrite(pynini.cross("[E1]", "[E1*]"), "1", _digit, _sigma_star)

# the actual factorizer
_phi = (_pad_zeros @ _raw_factorizer @ _del_zeros @ _fix_teens).optimize()

_lambda = pynini.string_map(
    [
        ("1", "one"),
        ("2", "two"),
        ("3", "three"),
        ("4", "four"),
        ("5", "five"),
        ("6", "six"),
        ("7", "seven"),
        ("8", "eight"),
        ("9", "nine"),
        ("1[E1]", "ten"),
        ("1[E1*]1", "eleven"),
        ("1[E1*]2", "twelve"),
        ("1[E1*]3", "thirteen"),
        ("1[E1*]4", "fourteen"),
        ("1[E1*]5", "fifteen"),
        ("1[E1*]6", "sixteen"),
        ("1[E1*]7", "seventeen"),
        ("1[E1*]8", "eighteen"),
        ("1[E1*]9", "nineteen"),
        ("2[E1]", "twenty"),
        ("3[E1]", "thirty"),
        ("4[E1]", "forty"),
        ("5[E1]", "fifty"),
        ("6[E1]", "sixty"),
        ("7[E1]", "seventy"),
        ("8[E1]", "eighty"),
        ("9[E1]", "ninety"),
        ("[E2]", "hundred"),
        ("[E3]", "thousand"),
        ("[E6]", "million"),
    ]
)
_lambda_star = pynutil.join(_lambda, pynutil.insert(" ")).optimize()


def number(token: str) -> str:
    return rewrite.one_top_rewrite(token, _phi @ _lambda_star)


if __name__ == "__main__":
    pairs = [
        (324, "three hundred twenty four"),
        (314, "three hundred fourteen"),  # Forcing newline.
        (3014, "three thousand fourteen"),
        (30014, "thirty thousand fourteen"),
        (300014, "three hundred thousand fourteen"),
        (3000014, "three million fourteen"),
    ]
    for (num, name) in pairs:
        prediction = number(str(num))
        print(prediction)
