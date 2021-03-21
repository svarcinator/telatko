import spot
import sys
import argparse
import os
from qbf.q_main import play, print_aut
from telatko2.playground import process_automaton


def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-F",
        "--autfile",
        help="File containing automata in HOA format.")
    parser.add_argument("-O", "--outfile", help="File to print output to.")
    parser.add_argument("-M", "--mode", help="Level of simplification.")
    args = parser.parse_args()
    if not args.autfile:
        print("No automata to process.", file=sys.stderr)
    if not args.mode:
        mode = '0'

    aut = spot.automata(args.autfile)

    for a in aut:

        origin = spot.automaton(a.to_str())
        print_aut(origin, "problem", "w")
        try:
            spot.cleanup_acceptance_here(a)
            process_automaton(a)
            if args.mode != '0':
                acc_sets_count = a.get_acceptance().used_sets().count()
                clauses_count = max(len(a.get_acceptance().top_disjuncts()), len(a.get_acceptance().top_conjuncts()))
                print("formula:", a.get_acceptance(), "C:", clauses_count, "K:", acc_sets_count)

                if acc_sets_count == 0:
                    auto = a
                else:
                    auto = play(a, clauses_count, acc_sets_count, args.mode)
            else:
                auto = a

            if args.outfile:
                print_aut(auto, args.outfile, "a")
            else:
                print_aut(auto, None, " ")

            if not spot.are_equivalent(auto, origin):
                print("nejsou ekvivalentni")
                return

            else:
                print("ekvivalentni")

        except RuntimeError:  # too many marks
            print(
                "Automaton has too many acceptance sets, 32 is the limit.",
                file=sys.stderr)

    
if __name__ == "__main__":
    main(sys.argv[1:])