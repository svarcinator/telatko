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
        "-F1",
        "--autfile1",
        help="File containing automata in HOA format.")
    parser.add_argument(
        "-F2",
        "--autfile2",
        help="File containing automata in HOA format.")
    args = parser.parse_args()


    if not args.autfile1 or not args.autfile2:
        print("No automata to process.", file=sys.stderr)


    aut1 = spot.automata(args.autfile1)
    aut2 = spot.automata(args.autfile2)


    for a1 in aut1:
        for a2 in aut2:
            try:
                if spot.are_equivalent(a1, a2):
                    print("EQUIVALENT")
                    return 0
                else:
                    print("NOT-EQUIVALENT")
                    return -1


            except RuntimeError as e:  # too many marks
                print(
                    "Automaton has too many acceptance sets, 32 is the limit.",
                    file=sys.stderr)


if __name__ == "__main__":
    main(sys.argv[1:])
