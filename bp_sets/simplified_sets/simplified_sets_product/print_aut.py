import spot
import sys
import argparse
import os


def print_aut(aut, output, m):
    """
    Prints automata to given output
    Args:
        aut:
        output:
        m: mode

    Returns:

    """
    if output is not None:
        f = open(output, m)
        f.write(aut.to_str() + '\n')
        f.close()
    else:
        print(aut.to_str())

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

    args = parser.parse_args()

    if not args.autfile:
        print("No automata to process.", file=sys.stderr)

    aut = spot.automata(args.autfile)

    for a in aut:
        try:
            if args.outfile:
                print_aut(a, args.outfile, "a")
            else:
                print_aut(a, None, " ")


        except BaseException as err:
            print(f"Unexpected {err=}, {type(err)=}")

        except RuntimeError as e:  # too many marks
            """print(
                "Automaton has too many acceptance sets, 32 is the limit.",
                file=sys.stderr)
                """



if __name__ == "__main__":
    main(sys.argv[1:])
