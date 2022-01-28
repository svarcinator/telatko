import spot
import sys
import argparse
import os

from qbf.q_main import print_aut

def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-F",
        "--autfile",
        help="File containing automata in HOA format.")
    parser.add_argument("-O", "--outfile", help="File to print output to.", default=None)
    parser.add_argument(
        "-P",
        "--product",
        help="Product -- union/intersection", choices=['or', 'and'], default='or')

    args = parser.parse_args()



    if not args.autfile:
        print("No automata to process.", file=sys.stderr)

    aut = spot.automata(args.autfile)

    for a in aut:
        for b in aut:
            if a == b:
                continue
            if args.product == 'or':
                res = spot.product_or(a, b)
            else:
                res = spot.product(a, b)

            if args.outfile:
                print_aut(res, args.outfile, "a")
            else:
                print_aut(res, None, " ")


if __name__ == "__main__":
    main(sys.argv[1:])
