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
    parser.add_argument("-T", "--timeout", help="Kill QBF solver after inserted number of seconds")
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
        print_aut(origin, "problem", "w")
        try:
            spot.cleanup_acceptance_here(a)

            a = process_automaton(a)

            acc_sets_count = a.get_acceptance().used_sets().count()
            clauses_count = len(a.get_acceptance().to_dnf().top_disjuncts())
            print("formula:", a.get_acceptance(), "C:", clauses_count, "K:", acc_sets_count)


            if mode >=2 and mode <= 4:
                if acc_sets_count == 0:
                    auto = a
                else:
                    auto = play(a, clauses_count, acc_sets_count, mode, timeout)
                    # auto = process_automaton(auto)

            else:
                auto = a
            clauses_count2 = max(len(auto.get_acceptance().top_disjuncts()),
                                 len(auto.get_acceptance().top_conjuncts()))

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