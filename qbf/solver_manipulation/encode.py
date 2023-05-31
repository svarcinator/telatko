

import subprocess
from telatko2.classes import SATformula, safe_file
import re


def encode_qdimacs(boole_formula_path: str) -> str:
    """
        return :str name of qdimacs file
    """
    print(f"booleguru formula path : {boole_formula_path} ")

    try:

        cp = subprocess.run(["./../solvers/booleguru/build/booleguru",
                             boole_formula_path,
                             "--qdimacs"],
                            universal_newlines=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            timeout=20)

    except subprocess.TimeoutExpired:
        print("expired")
        return
    except BaseException:
        print("Booleguru error")
        return

    qdimacs_file_path = "./qbf/solver_manipulation/formulas_files/qbf_formula.qdimacs"

    safe_file(qdimacs_file_path, cp.stdout, "w")

    return qdimacs_file_path


def decode_qdimacs(qdimacs_path: str):
    """
        Booleguru encodes mapping of original variables to numbers
        into the comments in the beginning of the file.
    """
    re_pattern = "c.*"
    f = open(qdimacs_path, "r")
    qdim_query = [line for line in f.readlines() if re.match(re_pattern, line)]
    f.close()

    return qdim_query


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
    encode_qdimacs(f)


# test()
