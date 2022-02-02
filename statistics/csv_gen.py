import spot
import sys
import argparse
import os
import subprocess


def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-F",
        "--infile",
        help="Path to input file.")
    parser.add_argument(
        "-O",
        "--outfolder",
        help="File to print output to.",
        default=None)
    parser.add_argument(
        "-L1",
        "--level1",
        help="Level of simplification 1.",
        action='store_true')
    parser.add_argument(
        "-L2",
        "--level2",
        help="Level of simplification 2.",
        action='store_true')
    parser.add_argument(
        "-L3",
        "--level3",
        help="Level of simplification 3.",
        action='store_true')

    args = parser.parse_args()
    csv_output = args.outfolder + "/" + str(args.infile)

    if not args.infile:
        print("No automata to process.", file=sys.stderr)
    if args.level1:
        csv_output_l1 = csv_output + "L1.csv"
        astring = "autcross --file=" + str(args.infile) + " --tool='python3 ./main.py -F%H -O%O -L 1' --language-preserved --csv=" + csv_output_l1
        os.system(astring)
    if args.level2:
        csv_output_l2 = csv_output + "L2.csv"
        astring = "autcross --file=" + str(args.infile) + " --tool='python3 ./main.py -F%H -O%O -L 2' --language-preserved --csv=" + csv_output_l2
        os.system(astring)
    if args.level3:
        csv_output_l3 = csv_output + "L3.csv"
        astring = "autcross --file=" + str(args.infile) + " --tool='python3 ./main.py -F%H -O%O -L 3' --language-preserved --csv=" + csv_output_l3
        os.system(astring)


        """
        cp = subprocess.run(["autcross --file=", str(args.infile),
        "--tool='python3 ./main.py -F%H -O%O -L 1'--language-preserved --csv="
        , args.outfile],
         universal_newlines=True,
         stdout=subprocess.PIPE,
         stderr=subprocess.PIPE)
         """


if __name__ == "__main__":
    main(sys.argv[1:])
