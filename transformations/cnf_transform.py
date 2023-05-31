from telatko2.classes import SATformula
from copy import deepcopy
from transformations.tseitin import *
from typing import Callable
import subprocess
import sys
sys.path.append('..')


class Transform:
    def __init__(self, formula):
        self.formula = formula

    def __str__(self):
        return str(self.formula)

    def eliminate_implication_init(self):
        self.eliminate_implication_rec(self.formula)

    def eliminate_implication(self):
        self.eliminate_implication_init()

    def eliminate_implication_rec(self, ast):
        #print(f"ast before {ast}")
        if ast.operator == "->":
            assert(len(ast.subformula) == 2)
            ast.set_op("|")
            ast.subformula[0].negate()
        #print(f"ast after {ast}")
        for subf in ast.subformula_list():
            self.eliminate_implication_rec(subf)

    def eliminate_equivalence(self):
        self.eliminate_equivalence_init()

    def eliminate_equivalence_init(self):
        self.eliminate_equivalence_rec(self.formula)

    def eliminate_equivalence_rec(self, ast):
        #print(f"ast before {ast}")
        if ast.operator == "<->":
            assert(len(ast.subformula) == 2)
            ast.set_op("&")

            left = deepcopy(ast.subformula[0])
            right = deepcopy(ast.subformula[1])
            right.negate()
            l_notr = SATformula("|", [deepcopy(left), deepcopy(right)])
            right.negate()
            left.negate()
            notl_r = SATformula("|", [deepcopy(left), deepcopy(right)])
            ast.subformula = [l_notr, notl_r]

        #print(f"ast after {ast}")
        for subf in ast.subformula_list():
            self.eliminate_equivalence_rec(subf)

    def distribute_not(self):
        self.distribute_not_init()

    def distribute_not_init(self):
        self.distribute_not_rec(self.formula)
        # self.formula.print_info()

    def distribute_not_rec(self, ast):

        #assert(ast.get_op() == ("&" or "|") )
        # print(ast)

        if ast.is_negated() and not ast.is_empty():
            if ast.get_op() == "&":
                ast.set_op("|")
            else:
                ast.set_op("&")
            ast.negate()
            for subf in ast.subformula_list():
                subf.negate()

        for subf in ast.subformula_list():
            self.distribute_not_rec(subf)

    def negation_nf(self, check_equivalence: bool = False):
        if check_equivalence:
            _, old_body = self.formula.get_prefix_and_nonprefix_part()
            old_body = deepcopy(old_body)
        self.eliminate_implication()
        self.eliminate_equivalence()
        self.distribute_not()

        if check_equivalence:
            _, new_body = self.formula.get_prefix_and_nonprefix_part()
            assert(check_boole_formulas_equivalence(old_body, new_body))
            print("Negation NF equivalent")

        #print(f"in CNF transform : {self.formula}, address {id(self.formula)}")

    def tseitin(self):
        tseitin_handler = Tseitin_transform(deepcopy(self.formula))
        tseitin_handler.transform()
        self.formula = tseitin_handler.get_tseitin_formula()
        return self.formula

    def cnf_post_tseitin(self):
        prefix, body = self.formula.get_prefix_and_nonprefix_part()

        # root of ast is &
        assert(body.get_op() == "&" or body.is_leaf())

        new_subf_list = []

        for subf in body.subformula_list():
            if subf.get_op() == "h_0":
                new_subf_list.append(subf)
                continue

            # operator in depth 1 is either <-> or forrst tseitin variable (at
            # subformulas[0])

            assert(subf.get_op() == "<->")

            # shape h_i <-> ( l op r ), op in ["&", "|"]
            assert(len(subf.subformula_list()) == 2)
            right = subf.pop_subformula()
            h_i = subf.pop_subformula()

            if right.get_op() == "&":
                h_i.negate()
                for atom in right.subformula_list():

                    new_subf_list.append(SATformula(
                        "|", [deepcopy(h_i), deepcopy(atom)]))
                h_i.negate()
                right.negate()
                self.distribute_not_rec(right)
                right.add_subf(h_i)

                new_subf_list.append(right)
            else:
                for atom in right.subformula_list():

                    new_subf_list.append(
                        SATformula(
                            "|", [
                                deepcopy(h_i), SATformula(
                                    atom.get_op(), [], True, False, [])]))
                h_i.negate()
                right.add_subf(h_i)

                new_subf_list.append(right)

        body.subformula = new_subf_list
        if prefix:
            prefix.last_node().add_subf(body)
            self.formula = prefix
        else:
            self.formula = body

    def call_formula_transformation(
            self,
            func: Callable,
            check_equivalence: bool) -> bool:

        if check_equivalence:
            old_f = deepcopy(self.formula)

        func()
        new_f = self.formula

        if check_equivalence:
            _, old_body = old_f.get_prefix_and_nonprefix_part()
            _, new_body = new_f.get_prefix_and_nonprefix_part()
            assert(check_boole_formulas_equivalence(old_body, new_body))

    def cnf(self, check_equivalence: bool = False):
        print(f"Transforming formula {self.formula} to CNF")
        self.call_formula_transformation(self.negation_nf, check_equivalence)

        print(f"NNF {self.formula}")
        self.call_formula_transformation(self.tseitin, check_equivalence)
        print()
        print(f"Tseitin {self.formula}")
        self.formula.sanity_checks()

        self.call_formula_transformation(
            self.cnf_post_tseitin, check_equivalence)
        print()
        print(f"Final result {self.formula}")
        print()
        return self.formula


def check_boole_formulas_equivalence(f1: SATformula, f2: SATformula) -> bool:
    eq = SATformula("<->", [f1, f2])

    limb_f = open("eq_check.boole", "w")
    limb_f.write(str(eq))
    limb_f.close()

    try:
        cp = subprocess.run(["/home/ter/solvers/limboole1.2/limboole",
                             "./eq_check.boole"],
                            universal_newlines=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            timeout=30)

    except subprocess.TimeoutExpired:
        print("expired")
        return Solver_result.timeout, None

    out = cp.stdout.splitlines()
    if len(out) == 1:
        print(f"Formulas {f1} and {f2} are not equivalent.")
        return False

    if len(out) == 0:
        print("sat error")
        assert(False)
    return True


####### TEST ###############

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
        (a & b & c & d) -> (e & f & g)
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


def create_formula8():
    """
        (a & b) <-> (c | d)
    """
    left = SATformula("&", [SATformula("a"), SATformula("b")])
    right = SATformula("|", [SATformula("c"), SATformula("d")])
    return SATformula("<->", [left, right])


def create_formula9():
    """
        (a & b) <-> (c | d)
    """
    left = SATformula("<->", [SATformula("a"), SATformula("b")])
    left.negate()
    #right = SATformula("|", [SATformula("c"), SATformula("d")])
    return left


def create_formula10():
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

    f = create_formula10()
    print(f"formula : {f}, address {id(f)}")
    f.sanity_checks()
    transf = Transform(f)
    # transf.cnf(check_equivalence=True)
    transf.negation_nf()

    f.sanity_checks()
    assert(f.check_nnf())

    print(f"formula : {f}, address {id(f)}")
    return
    #cnf_f = transf.get_formula()
    cnf_f.sanity_checks()
    assert(cnf_f.check_nnf())

    assert(cnf_f.check_cnf())


#
