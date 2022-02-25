import spot
import sys
import argparse
import os

from telatko2.classes import FormulaAtribute
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
        default=1)
    parser.add_argument(
        "-T",
        "--timeout",
        help="Kill QBF solver after inserted number of seconds.", type=int, default=50)
    parser.add_argument(
        "-S",
        "--scc",
        help="Use SCC optimization.", action='store_true')
    parser.add_argument(
        "-M",
        "--minimized_atribut",
        help="Acceptance condition atribute we want to minimize.", choices=['clauses', 'acc_marks', 'all'], default='acc_marks')
    parser.add_argument(
        "-Q",
        "--qbf_solver",
        help="Choose wchich solver is going to be used.", choices=['limboole', 'z3'], default='limboole')

    args = parser.parse_args()


    if not args.autfile:
        print("No automata to process.", file=sys.stderr)

    aut = spot.automata(args.autfile)
    timeouted = [0]

    for a in aut:

        origin = spot.automaton(a.to_str())
        #tmp_a = spot.automaton(a.to_str())
        print_aut(origin, "problem", "w")
        try:
            spot.cleanup_acceptance_here(a)

            #a_tele = process_automaton(tmp_a)

            acc_sets_count = a.get_acceptance().used_sets().count()
            clauses_count = len(
                a.get_acceptance().to_dnf().top_disjuncts())
            if args.level > 3:
                args.level = 3

            if args.level >= 1 and args.level <= 4:

                if acc_sets_count == 0:
                    auto = a
                else:

                    auto = play(
                        a, clauses_count, acc_sets_count, args.level, args.timeout, timeouted, args.scc, args.minimized_atribut, args.qbf_solver)
                    """
                    if a_tele.get_acceptance().used_sets().count() < auto.get_acceptance().used_sets().count():
                        print_aut(origin, "better_tele_l1.hoa", "a")
                    """

            else:
                auto = a

            if args.outfile:
                print_aut(auto, args.outfile, "a")
            else:
                print_aut(auto, None, " ")

            if not spot.are_equivalent(origin, auto):
                print("not equivalent")
                print_aut(origin, "not_eq", "w")
                print("timeouted:", timeouted[0])
                return
            else:
                print("equivalent")

            acc_sets_count2 = auto.get_acceptance().used_sets().count()

        # except BaseException as err:
            #print(f"Unexpected {err=}, {type(err)=}")

        except RuntimeError as e:  # too many marks
            print(
                "Automaton has too many acceptance sets, 32 is the limit.",
                file=sys.stderr)

    print("timeouted:", timeouted[0])


if __name__ == "__main__":
    main(sys.argv[1:])
