from transformations.cnf_transform import *
from telatko2.classes import SATformula
import sys
sys.path.append('..')


class Qdimacs_transform:
    def __init__(self, formula):
        self.boole_formula = formula
        self.mapping = {}
        self.qdim_body: [str] = []
        self.qdim_prefix = []
        self.new_var_num = 1
        self.preamble = None  # (number of atoms, number of clauses)

    def check_cnf(self) -> bool:
        if not self.boole_formula.check_cnf():
            print("Formula is not in CNF")
            return False
        return True

    # create qdimacs formula

    def create_atom_var(self, var: str, negated: bool = False) -> int:
        """
            var : variable in boole format
            Get variable from map (or create mapping it).
        """

        n = 0

        if var in self.mapping:
            n = self.mapping[var]
        else:
            self.mapping[var] = self.new_var_num
            n = self.new_var_num
            self.new_var_num += 1
        return n * -1 if negated else n

    def create_qdim_disjunct(self, ast: SATformula):

        assert(ast.get_op() == "|")
        disj_list = []

        for child in ast.subformula_list():
            var_num = self.create_atom_var(child.get_op(), child.is_negated())
            disj_list.append(var_num)
        self.qdim_body.append(disj_list)

    def create_qdim_body(self, ast: SATformula):

        if not self.check_cnf():
            return

        if ast.is_leaf():
            # creates qdim variable and returns it
            var_num = self.create_atom_var(
                var=ast.get_op(), negated=ast.is_negated())
            self.qdim_body.append([var_num])

        elif ast.get_op() == "|":
            # formula of the form : (a | b | c)
            self.create_qdim_disjunct(ast)
        else:
            # formula of the fotm (a | b) & (c | d) & e
            for child in ast.subformula_list():
                self.create_qdim_body(child)

    def create_qdim_quant_part(self, quant_ast: SATformula):
        if not quant_ast:
            # no quantified prefix (quant_ast == None)
            return
        assert(quant_ast.is_quantified())
        q_numbers = []
        for var in quant_ast.quantified_vars:
            q_numbers.append(self.create_atom_var(var))
        self.qdim_prefix.append(
            ("a" if quant_ast.get_op() == "#" else "e", q_numbers))

        for child in quant_ast.subformula_list():
            self.create_qdim_quant_part(child)

    def create_preamble(self):
        self.preamble = (self.new_var_num - 1, len(self.qdim_body))

    def create_qdimacs(self) -> None:

        prefix, body = self.boole_formula.get_prefix_and_nonprefix_part()
        self.create_qdim_quant_part(prefix)
        self.create_qdim_body(body)
        self.create_preamble()

        print(self.mapping)

    # write qdimacs to file
    def write_preamble(self, filename: str) -> None:
        f = open(filename, "w")
        f.write(f"p cnf {self.preamble[0]} {self.preamble[1]}\n")
        f.close()

    def write_prefix(self, filename: str) -> None:
        f = open(filename, "a")
        for q_entry in self.qdim_prefix:
            # q_entry = ("a"/"e", [quantified variables])
            line = " ".join(str(num) for num in q_entry[1])

            f.write(f"{q_entry[0]} {line} 0\n")
        f.close()

    def write_body(self, filename: str) -> None:
        f = open(filename, "a")
        for disjunct in self.qdim_body:
            # disjunct = [vars]
            f.write(f"{' '.join(str(num) for num in disjunct)} 0\n")

    def qdimacs_to_file(self, filename: str) -> None:
        self.write_preamble(filename)
        self.write_prefix(filename)
        self.write_body(filename)


def create_formula1():
    return SATformula("a", [], True, False, [])


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

    f = create_formula1()
    f.sanity_checks()
    transf = CNF_transform(f)
    transf.cnf(check_equivalence=True)
    cnf_f = transf.get_formula()
    cnf_f.sanity_checks()
    assert(cnf_f.check_nnf())

    assert(cnf_f.check_cnf())

    trans_q = Qdimacs_transform(cnf_f)
    trans_q.create_qdimacs()

    trans_q.qdimacs_to_file("formula.qdimacs")


# test()
