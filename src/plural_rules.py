import pynini


chars = (
    [chr(i) for i in range(1, 91)]
    + [r"\[", r"\\", r"\]"]
    + [chr(i) for i in range(94, 256)]
)
sigma_star = pynini.union(*chars).closure()

singular_map = pynini.union(
    pynini.cross("feet", "foot"),
    pynini.cross("pence", "penny"),
    # any sequence of bytes in "ches" strips the "es"
    sigma_star + pynini.cross("ches", "ch"),
    # any sequence of bytes ending in "s" strips the "s"
    sigma_star + pynini.cross("s", ""),
)

# define context-dependent rewrite that performs
# TODO: context " 1 __ches." or " 1 feet?" => " 1 foot?"
rc = pynini.union(".", ",", "!", ";", "?", " ", "[EOS]")
singularize_var = pynini.cdrewrite(singular_map, " 1 ", rc, sigma_star)


def singularize(string):
    return pynini.shortestpath(pynini.compose(string.strip(), singularize_var)).string()


result = singularize("The current temperature in New York is 1 degrees")
print(result)
