import pynini
import pynini as pn
from pynini.lib import pynutil, rewrite

chars = (
    [chr(i) for i in range(1, 91)]
    + [r"\[", r"\\", r"\]"]
    + [chr(i) for i in range(94, 256)]
)
sigma_star = pynini.union(*chars).closure()


def example():
    s = "How are you"
    x = pn.acceptor(s)
    print(x)

    ASCII_STRINGS = ["ha ha", "who?", "Capitals!", "`1234567890~!@#$%^&*()"]
    NON_ASCII_CHARS = ["é", "ב", "क", "€", "д", "零"]
    UTF8_STRINGS = ["Who?", "¿Quién?", "ארה״ב", "हिन्दी", "今日はそれがググりました。"]


def fsa_a2b(input: str):
    # contruct FSA containing the inputs strings
    sigma = pn.union("a", "b", "c").closure()

    # construct a FST representing the rule
    tau = pn.cross("a", "b")
    # compute compostion A@B extract the path
    rule = pn.cdrewrite(tau, "c", "c", sigma)

    lattice = pn.compose(input, rule)
    print(lattice.string())


def string_tagging(input_string: str):
    # mention of a various types of cheese
    # output: Do you have <cheese>Camembert</cheese> or <cheese>Edam</cheese>?
    cheeses = (
        "Boursin",
        "Camembert",
        "Cheddar",
        "Edam",
        "Gruyere",
        "Ilchester",
        "Jarlsberg",
        "Red Leicester",
        "Stilton",
    )

    # construct transducers insert the left and right tags
    fst_target = pynini.string_map(cheeses)
    ltag = pynini.cross("", "<cheese>")
    rtag = pynini.cross("", "</cheese>")
    substitution = ltag + fst_target + rtag

    rewrite = pynini.cdrewrite(substitution, "", "", sigma_star)
    output = pynini.compose(input_string, rewrite).string()
    # output = pynini.shortestpath(pynini.compose(input_string, rewrite)).string()
    print(output)


def test(input_string):
    graph_digit = pn.string_file("data/en.tsv")
    graph_hundred = pynini.cross("trăm", "")
    NEMO_WHITE_SPACE = pynini.union(" ", "\t", "\n", "\r", u"\u00A0").optimize()
    delete_space = pynutil.delete(pynini.closure(NEMO_WHITE_SPACE))
    graph_hundred_component = pynini.union(
        graph_digit + delete_space + graph_hundred, pynutil.insert("0")
    )
    rewrite = pynini.cdrewrite(graph_hundred_component, "", "", sigma_star)
    output = pynini.compose(input_string, rewrite).string()
    print(output)


if __name__ == "__main__":
    # example()

    input_string = "Do you have Camembert or Edam?"
    string_tagging(input_string)
    #
    # input_string = "caccac"
    # fsa_a2b(input_string)

    # error????
    # test("một trăm nghìn")
