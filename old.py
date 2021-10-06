import spot
import sys
import argparse
import os
from qbf.classes import *
import re

def inf_set_old_formula(edge_dict, set_num):
    new_shape = SATformula('|')
    for edge in edge_dict[set_num]:
        new_shape.add_subf(
            SATformula(
                "e_" +
                str(edge)))
    return new_shape

def fin_set_old_formula(edge_dict, set_num):
    new_shape = SATformula('&')
    for edge in edge_dict[set_num]:
        new_shape.add_subf(
            SATformula(
                "!e_" +
                str(edge)))
    return new_shape


def old_formula(acc, edge_dict):
    """

        Args:
            acc: Original acceptance condition in DNF
            edge_dict: Dictionary with number of acceptance set : numbers of edges that the acceptance set contains

        Returns: Formula in DNF

        """

    sets = acc.used_inf_fin_sets()
    inf_sets = list(sets[0].sets())
    fin_sets = list(sets[1].sets())
    print(inf_sets)
    formula = str(acc)

    for i in inf_sets:
        reg = "Inf\(" + str(i) + "\)"
        formula = re.sub(reg, str(inf_set_old_formula(edge_dict, i)), formula)
    for f in fin_sets:
        reg = "Fin\(" + str(f) + "\)"
        formula = re.sub(reg, str(fin_set_old_formula(edge_dict, f)), formula)
        
    return SATformula(formula)



    print(formula)


    """
    dnf_formula = SATformula('|')
    for dis in acc.formula:
        conjunct_f = SATformula('&')
        for con in dis:
            new_shape = None
            if con.type == MarkType.Inf:
                new_shape = SATformula('|')
                for edge in edge_dict[con.num]:
                    new_shape.add_subf(
                        SATformula(
                            "e_" +
                            str(edge)))
            else:
                new_shape = SATformula('&')
                for edge in edge_dict[con.num]:
                    new_shape.add_subf(
                        SATformula(
                            "!e_" + str(edge)))
            conjunct_f.add_subf(new_shape)
        dnf_formula.add_subf(conjunct_f)

    return dnf_formula
    """





def edge_dictionary(aut):
    """

    Args:
        aut: spot::twa - automaton from input

    Returns: Dictionary {acceptance set number : [numbers of edges in this set]}

    """
    list_of_all_edges = aut.edges()
    edge_dict = {}
    set_nums = aut.get_acceptance().used_sets()

    for acc_set in set_nums.sets():
        edge_dict[acc_set] = list(map(aut.edge_number, list(
            filter(lambda edg: edg.acc.has(acc_set), list_of_all_edges))))
    return edge_dict


def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-F",
        "--autfile",
        help="File containing automata in HOA format.")
    parser.add_argument("-O", "--outfile", help="File to print output to.")
    parser.add_argument("-L", "--mode", help="Level of simplification.")
    parser.add_argument(
        "-T",
        "--timeout",
        help="Kill QBF solver after inserted number of seconds")
    args = parser.parse_args()
    if not args.autfile:
        print("No automata to process.", file=sys.stderr)
    timeout = args.timeout
    if not args.timeout:
        timeout = 50
    if not args.mode:
        mode = 1
    else:
        mode = int(args.mode)

    aut = spot.automata(args.autfile)

    for a in aut:

        origin = spot.automaton(a.to_str())

        try:
            spot.cleanup_acceptance_here(a)
            edge_dict = edge_dictionary(a)
            acc = old_formula(a.get_acceptance(), edge_dict)


        except RuntimeError:  # too many marks
            print(
                "Automaton has too many acceptance sets, 32 is the limit.",
                file=sys.stderr)


if __name__ == "__main__":
    main(sys.argv[1:])
