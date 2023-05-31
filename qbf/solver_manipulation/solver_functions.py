import subprocess
from z3 import *
import time
from telatko2.classes import Solver_result, SATformula, safe_file
from qbf.solver_manipulation.encode import encode_qdimacs, decode_qdimacs
from transformations.qcir import *
from typing import List


COUNTER = 0


def booleguru_translate(out_path):
    global COUNTER

    try:
        cp = subprocess.run(["./../solvers/booleguru/build/booleguru",
                             "./qbf_formula.boole",
                             "--qdimacs"],
                            universal_newlines=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            timeout=3)
        cp2 = subprocess.run(
            [
                "./../solvers/booleguru/build/booleguru",
                "./qbf_formula.boole",
                "--qcir"],
            universal_newlines=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=3)
    except subprocess.TimeoutExpired:
        print("expired")
        return

    safe_file(f"{out_path}/qdimacs/telatko{COUNTER}.qdimacs", cp.stdout, "w")
    safe_file(f"{out_path}/qcir/telatko{COUNTER}.qcir", cp2.stdout, "w")

    COUNTER += 1


def z3_result(result, model=None):

    if result == sat:
        return Solver_result.sat, model, None
    elif result == z3.unknown:
        return Solver_result.timeout, None, None
    elif result == unsat:
        return Solver_result.unsat, None, None
    assert(False)


def query(formula, formula_attr):
    formula_file_path = "./qbf/solver_manipulation/formulas_files/qbf_formula.boole"

    if formula_attr.solver == "z3":
        solver = Solver()
        solver.add(formula)
        solver.set("timeout", 1000 * formula_attr.timeout)
        solver.push()
        result = solver.check()
        model = None
        if result == sat:
            model = solver.model()
        return z3_result(result, model)
    elif formula_attr.solver == "quabs":

        qcir_c = Qcir_ctor(formula)
        qcir_c.to_qcir("./qbf/solver_manipulation/formulas_files/formula.qcir")
        return Solver_result.unsat, None
    elif formula_attr.solver == "caqe":
        safe_file(formula_file_path, str(formula), "w")
        formula_file_path = encode_qdimacs(formula_file_path)
        tool_path = "./../solvers/caqe/target/release/caqe"
    else:
        # Limboole solver
        safe_file(formula_file_path, str(formula), "w")
        tool_path = "./../solvers/limboole1.2/limboole"

        #elapsed = -1

    command = [tool_path]
    if formula_attr.solver == "caqe":
        command.append("--qdo")
    command.append(formula_file_path)

    try:
        #start = time.time()

        cp = subprocess.run(command,
                            universal_newlines=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            timeout=formula_attr.timeout)
        print("Call done")
        #elapsed = (time.time() - start)

    except subprocess.TimeoutExpired:
        print("expired")
        return Solver_result.timeout, None, None

    except BaseException:
        print(
            "Subprocess running solver failed. Be sure that solver is installed in ./../solvers/{tool_file}")
        return Solver_result.unsat, None, None

    out = cp.stdout.splitlines()

    if len(out) == 1 or out[-1] != 'c Satisfiable':
        print("unsatisfiable")
        return Solver_result.unsat, None, None

    if len(out) == 0:
        print("sat error")
        assert(False)

    model = out[1:]

    var_mapping = decode_qdimacs(
        formula_file_path) if formula_attr.solver == "caqe" else None
    return Solver_result.sat, model, var_mapping
