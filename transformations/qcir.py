from telatko2.classes import SATformula, safe_file
from transformations.cnf_transform import *
import sys
sys.path.append('..')


class Qcir_ctor:
    def __init__(self, formula):
        self.formula = formula
        self.new_var_num = 1
        self.free_vars = set()
        self.body = []  # will contain qcir lines representing body of a formula
        self.var_dict = {}

    def to_nnf(self):
        t = Transform(self.formula)
        t.negation_nf(True)

    def get_fresh_var(self) -> str:
        """
            Return str fresh variable t_n
            and increment self.new_var - smallest unused var num
        """
        self.new_var_num += 1
        return self.new_var_num - 1

    def write_headline(self, file_handle):
        file_handle.write("#QCIR-G14\n")

    def add_var_to_dict(self, var: str, negated: bool = False) -> str:
        if var in self.var_dict:
            return str(-1 * self.var_dict[var]
                       if negated else self.var_dict[var])
        self.var_dict[var] = self.get_fresh_var()

        return str(-1 * self.var_dict[var] if negated else self.var_dict[var])

    def encode_prefix(self, prefix_ast: SATformula, file_handle):
        if prefix_ast.operator == "#":
            file_handle.write(
                f"forall({','.join(map(self.add_var_to_dict, prefix_ast.quantified_vars))})\n")
        else:
            file_handle.write(
                f"exists({','.join(map(self.add_var_to_dict, prefix_ast.quantified_vars))})\n")
        for child in prefix_ast.subformula:
            self.encode_prefix(child, file_handle)

    def encode_output(self, file_handle, var: str):
        """
            Returns main variable
        """

        file_handle.write(f"output({var})\n")

    def encode_body_rec(self, ast: SATformula) -> str:
        if ast.is_leaf():
            # we need to keep check of free variables, every var beginning on
            # other letter is quantified
            if ast.operator[0] in ['f', 'p', 'n']:
                #print(f"adding free var {ast} first letter {ast.operator[0]} ")
                self.free_vars.add(self.add_var_to_dict(ast.operator))
            return self.add_var_to_dict(ast.operator, ast.negation)

        children_vars = []

        if len(ast.subformula) < 2:
            print(
                f"short subf: {ast}, is leaf {ast.is_leaf()} subf {ast.subformula[0]} op {ast.operator} {ast.subformula}")

        for child in ast.subformula:
            children_vars.append(self.encode_body_rec(child))
        ast_var = str(self.get_fresh_var())

        self.body.append(
            f"{ast_var} = {'and' if ast.operator == '&' else 'or'}({', '.join(children_vars)})\n")
        return ast_var

    def write_free_vars(self, file_handle):
        file_handle.write(f"free({', '.join(self.free_vars)})\n")

    def qcir_file(self, filename):
        file_handle = open(filename, "w")

        self.write_headline(file_handle)

        prefix, body = self.formula.get_prefix_and_nonprefix_part()

        main_var = self.encode_body_rec(body)
        self.write_free_vars(file_handle)
        self.encode_prefix(prefix, file_handle)
        self.encode_output(file_handle, main_var)
        file_handle.writelines(self.body)
        # print(self.body)

        file_handle.close()

    def to_qcir(self, filename="formula.qcir"):
        print(self.formula)
        self.formula.sanity_checks()
        self.to_nnf()
        # self.formula.sanity_checks()
        # self.formula.check_nnf()
        print(self.formula)
        self.qcir_file(filename)


def test():
    f = create_formula10()
    print(f"Formula: {f}, address {id(f)}")
    qcir_c = Qcir_ctor(f)
    qcir_c.to_qcir()

    print(f"Formula: {qcir_c.formula}, address {id(qcir_c.formula)}")

# test()
