#!/usr/bin/env python3

import spot
import sys
import argparse
import os

from telatko2.classes import Switches
from qbf.q_main import play, print_aut
from telatko2.playground import process_automaton


def parser(argv):
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
        "-I",
        "--incremental",
        help="Use incremental solving.", action='store_true')
    parser.add_argument(
        "-G",
        "--gradual",

        help="Levels will gradually grow from L1 up to specified level.", action='store_true')

    parser.add_argument(
        "-M",
        "--solver",
        help="Choose solver",
        choices=['limboole', 'z3', 'quabs', 'caqe', 'booleguru + caqe'],
        default='z3')



    args = parser.parse_args()
    return args


def main(argv):
    args = parser(argv)

    if not args.autfile:
        print("No automata to process.", file=sys.stderr)

    # if no arguments given, default variant is gradually go up to level 3

    if args.level == 0 and not args.gradual and not args.incremental and not args.scc and args.solver == "z3":

        args.gradual = True
        args.level = 3
        args.incremental = True
        args.scc = True
    elif args.level == 0:
        args.gradual = True
        args.level = 3

    if args.level > 3:
        args.level = 3

    aut = spot.automata(args.autfile)
    formula_attributes = Switches(args)
    # formula_attributes.print_settings()

    for a in aut:

        origin = spot.automaton(a.to_str())
        try:
            spot.cleanup_acceptance_here(a)
            formula_attributes.set_C(a)

            if a.get_acceptance().used_sets().count() == 0:
                auto = a
            else:
                auto = play(a, formula_attributes)

            if args.outfile:
                print_aut(auto, args.outfile, "a")
            else:
                print_aut(auto, None, " ")


            #if not spot.are_equivalent(origin, auto):
            #    print("NOT EQUIVALENT!")
            #    assert (False)


        # except BaseException as err:
            # print(f"Unexpected {err=}, {type(err)=}")

        except RuntimeError as e:  # too many marks
            print(
                "Automaton has too many acceptance sets, 32 is the limit.",
                file=sys.stderr)


if __name__ == "__main__":
    main(sys.argv[1:])
