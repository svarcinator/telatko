#!/usr/bin/env python3

import spot
import sys
import argparse
import os

from telatko2.classes import Switches
from qbf.q_main import play, print_aut
from telatko2.playground import process_automaton


def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-F",
        "--autfile",
        help="File containing automata in HOA format.")
    parser.add_argument(
        "-O",
        "--outfile",
        help="File to print output to.",
        default=None)
    parser.add_argument(
        "-L",
        "--level",
        help="Level of simplification.",
        type=int,
        default=0)
    parser.add_argument(
        "-T",
        "--timeout",
        help="Kill QBF solver after inserted number of seconds.", type=int, default=50)
    parser.add_argument(
        "-S",
        "--scc",
        help="Use SCC optimization.", action='store_true')
    parser.add_argument(
        "-C",
        "--minimize_clauses",
        help="Turn on reduction of clauses.", action='store_true')
    parser.add_argument(
        "-B",
        "--base_level",
        help="Choose whether qbf level 1 or standard level 1(original TELAtko).", choices=['telatko', 'z3'], default='z3')
    parser.add_argument(
        "-I",
        "--incremental",
        help="Use incremental solving.", action='store_true')
    parser.add_argument(
        "-G",
        "--gradual",
        help="Levels will gradually grow from L1 up to specified level.", action='store_true')
    args = parser.parse_args()

    if not args.autfile:
        print("No automata to process.", file=sys.stderr)

    if args.level == 0:
        args.gradual = True
        args.level = 3

    if args.level > 3:
        args.level = 3

    aut = spot.automata(args.autfile)
    formula_attributes = Switches(args)

    for a in aut:

        origin = spot.automaton(a.to_str())
        try:
            spot.cleanup_acceptance_here(a)
            acc_sets_count = a.get_acceptance().used_sets().count()
            clauses_count = len(
                a.get_acceptance().to_dnf().top_disjuncts())
            formula_attributes.set_C(a)

            if args.base_level == "telatko":
                a = process_automaton(a)
                if args.level > 1 and a.get_acceptance().used_sets().count() != 0:
                    if formula_attributes.tmp_level != args.level:
                        formula_attributes.tmp_level = 2

                    auto = play(a, formula_attributes)
                else:
                    auto = a
            else:
                if a.get_acceptance().used_sets().count() == 0:
                    auto = a
                else:
                    auto = play(a, formula_attributes)

            if args.outfile:
                print_aut(auto, args.outfile, "a")
            else:
                print_aut(auto, None, " ")
            

            # if not spot.are_equivalent(origin, auto):
                # assert(False)

            acc_sets_count2 = auto.get_acceptance().used_sets().count()

        # except BaseException as err:
            #print(f"Unexpected {err=}, {type(err)=}")

        except RuntimeError as e:  # too many marks
            print(
                "Automaton has too many acceptance sets, 32 is the limit.",
                file=sys.stderr)


if __name__ == "__main__":
    main(sys.argv[1:])
