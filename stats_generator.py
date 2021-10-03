
def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-F",
        "--autfile",
        help="File containing automata in HOA format.")
    parser.add_argument("-N", "--name", help="Name of stats-files")
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
    cp = subprocess.run(["autcross", "--file=", args.autfile,  "--tool=",
    'python3 ./main.py -F%H -O%O -M 1',  "--language-preserved",  "--csv=", args.autfile + '.tele'
    "],
                        universal_newlines=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        timeout=int(timeout))
