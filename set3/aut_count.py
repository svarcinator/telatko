import spot
import argparse

def count_aut():
    parser=argparse.ArgumentParser()
    parser.add_argument("-F", "--autfile", help="hallp")
    args = parser.parse_args()
    aut = spot.automata(args.autfile)
    counter = 0
    for a in aut:
        counter += 1
    print("counter:", counter)

count_aut()
