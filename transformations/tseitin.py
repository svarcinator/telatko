from copy import deepcopy
from telatko2.classes import SATformula
import sys
sys.path.append('..')


class Tseitin_transform:
    """Transforms SATformula into Tseitin's encoding."""

    def __init__(self, sat_formula):
        self.old_formula = sat_formula
        self.tseitin_formula = SATformula("&", [])
        self.prefix = None
        self.new_var_index = 0

    def new_variable(self):

        var = SATformula("h_" + str(self.new_var_index), [])
        self.new_var_index += 1
        return var

    def skip_prefix(self, formula):

        while formula.is_quantified():
            # each quantifier has only one successor

            assert(len(formula.subformula_list()) == 1)
            prefix = deepcopy(formula)
            prefix.delete_subformulas()
            self.add_prefix(prefix)
            formula = formula.pop_subformula()

        return formula

    def quantify_tseitin_vars(self):

        if self.prefix:

            self.prefix.last_node().add_subf(
                SATformula(
                    "?",
                    subf_list=[],
                    negate=False,
                    quantifier=True,
                    quantified_vars=[
                        f"h_{i}" for i in range(
                            self.new_var_index)]))
        # if there is no prefix, all variables are outermost exist quantified
        # variables

    def transform_init(self):

        self.prefix, prefix_free_formula = self.old_formula.get_prefix_and_nonprefix_part()
        if prefix_free_formula.is_leaf():
            self.tseitin_formula = prefix_free_formula
        else:
            help_root = self.new_variable()
            self.tseitin_formula.add_subf(help_root)
            self.transform_rec(prefix_free_formula, SATformula(
                "<->", [deepcopy(help_root)]))

    def transform(self):
        self.transform_init()

        self.quantify_tseitin_vars()

    def transform_rec(self, old_root, new_tseitin_ekv):
        """
        old_root - root of original subformula
        new_tseitin_ekv - SATformula("<->", [h_i])
        """

        assert(not old_root.quantifier)

        new_root = SATformula(old_root.get_op(), [])
        if old_root.is_negated():
            new_root.negate()

        for subf in old_root.subformula_list():

            if subf.is_empty():
                new_root.add_subf(subf)
            else:
                help_var = self.new_variable()
                new_root.add_subf(help_var)
                self.transform_rec(subf, SATformula("<->", [help_var]))

        new_tseitin_ekv.add_subf(new_root)
        self.tseitin_formula.add_subf(new_tseitin_ekv)

    def get_tseitin_formula(self):
        if not self.prefix:

            return self.tseitin_formula
        p = self.prefix.last_node()
        p.add_subf(self.tseitin_formula)
        return self.prefix


###### TESTS ##########################

def create_formula1():
    """
        (a -> b) <-> (c | d)
    """
    left = SATformula("->", [SATformula("a"), SATformula("b")])
    right = SATformula("|", [SATformula("c"), SATformula("d")])
    return SATformula("<->", [left, right])


def create_formula2():
    """
        (a & b) | (c & d)
    """
    left = SATformula("&", [SATformula("a"), SATformula("b")])
    right = SATformula("&", [SATformula("c"), SATformula("d")])
    return SATformula("|", [left, right])


def create_formula3():
    """
        (a & b) -> (c | d)
    """
    left = SATformula("&", [SATformula("a"), SATformula("b")])
    right = SATformula("|", [SATformula("c"), SATformula("d")])
    return SATformula("->", [left, right])


def create_formula4():
    """
        (a | b)
    """
    f = SATformula("|", [SATformula("a"), SATformula("b")])
    return f


def create_formula5():
    """
        a
    """
    f = SATformula("a", [])
    f.negate()
    return f


def create_formula6():
    """
        (a & b & c & d) | (e & f & g)
    """
    left = SATformula("&",
                      [SATformula("a"),
                       SATformula("b"),
                          SATformula("c"),
                          SATformula("d")])
    right = SATformula(
        "&", [SATformula("e"), SATformula("f"), SATformula("g")])
    return SATformula("|", [left, right])


def create_formula7():
    """
        ?t ?u #x #y (a & b & c & (d|e)) -> ( f & g & h)
    """
    left = SATformula("&", [SATformula("a"), SATformula("b"), SATformula(
        "c"), SATformula("|", [SATformula("d"), SATformula("e")])])
    left.negate()
    right = SATformula(
        "&", [SATformula("f"), SATformula("g"), SATformula("h")])
    c = SATformula("->", [left, right])
    prefix = SATformula("#", [c], False, True, ["x", "y"])
    prefix2 = SATformula("?", [prefix], False, True, ["t", "u"])

    return prefix2


def test():
    f1 = create_formula7()
    tseit1 = Tseitin_transform(deepcopy(f1))

    tseit1.transform()
    #
    f = tseit1.get_tseitin_formula()
    print(f1)
    print(f)


# test()
