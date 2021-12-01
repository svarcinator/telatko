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
        "-A",
        "--autfile",
        help="File containing automata in HOA format.")
    parser.add_argument(
        "-B",
        "--b_autfile",
        help="File containing automata in HOA format.")
    parser.add_argument("-O", "--outfile", help="File to print output to.")
    print("cokoliv")
    args = parser.parse_args()
    
    aut1 = spot.automata(args.autfile)
    aut2 = spot.automata(args.b_autfile)
    print("aut1: " , aut1)
    for a in aut1:
    	for b in aut2:
    		product = spot.product_or(a, b)
    		
    		if args.autfile:
    			print_aut(product, args.outfile, 'a')
    		else:
    			print_aut(product, None, ' ')     
        

if __name__ == "__main__":
    main(sys.argv[1:])
    	    
    	    
        
