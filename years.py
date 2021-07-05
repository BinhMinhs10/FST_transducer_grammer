import os
import string
import pynini
from pynini.lib import byte, pynutil, rewrite

_lowercase = pynini.union(
    *[pynini.cross(x.upper(), x) for x in string.ascii_lowercase]
).closure()
_sigma_star = pynini.closure(byte.BYTE)
_tolower = pynini.cdrewrite(_lowercase, "", "", _sigma_star)


def get_abs_path(rel_path):
    """
    Get absolute path

    Args:
        rel_path: relative path to this file

    Returns absolute path
    """
    return os.path.dirname(os.path.abspath(__file__)) + "/" + rel_path


_digit = pynini.string_file(get_abs_path("data/zero.tsv"))

_year = pynini.union(
    pynutil.delete("năm ") +
    pynutil.insert("Năm ") +
    _digit + pynini.cross(" ", "") +
    _digit + pynini.cross(" ", "") +
    _digit + pynini.cross(" ", "") +
    _digit
)

_license = pynini.union(
    pynini.cross("bê ca ét", "BKS") + pynini.union(" ")
    + _digit + pynini.cross(" a", " A")
)


if __name__ == "__main__":

    text = """năm một chín chín bảy"""
    result = rewrite = pynini.cdrewrite(_year, "", "", _sigma_star)

    text = """bê ca ét năm a"""
    result = rewrite = pynini.cdrewrite(_license, "", "", _sigma_star)
    output = pynini.compose(text, rewrite).string()
    print(output)
