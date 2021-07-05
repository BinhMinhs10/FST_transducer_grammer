import pynini

# Constructing acceptors
# print(pynini.accep("Binh minh", token_type="utf8"))

bracket = pynini.accep("\[")


back_vowel = pynini.union("u", "o", "a")
neutral_vowel = pynini.union("i", "e")
front_vowel = pynini.union("y", "ö", "ä")
vowel = pynini.union(back_vowel, neutral_vowel, front_vowel)
archiphoneme = pynini.union("A", "I", "E", "O", "U")
consonant = pynini.union(
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
    "z",
)
sigma_star = pynini.union(vowel, consonant, archiphoneme).closure()
adessive = "llA"

intervener = pynini.union(consonant, neutral_vowel).closure()

adessive_harmony = (
    pynini.cdrewrite(pynini.cross("A", "a"), back_vowel + intervener, "", sigma_star)
    @ pynini.cdrewrite(pynini.cross("A", "ä"), "", "", sigma_star)
).optimize()


def make_adessive(stem):
    ur = stem + adessive
    sr = ur @ adessive_harmony
    return sr.string()


print(make_adessive("vero"))
print(make_adessive("käde"))
