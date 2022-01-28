import argparse
import sys
import numpy as np
import pandas as pd
import csv

def parse_csv(input_file):
    csv_file = pd.read_csv(input_file)

    # filter undesirable columns
    """
    filtered_columns_csv = csv_file.drop(columns=[ 'input.source','input.name', 'input.ap','input.edges', 'input.transitions', 'input.scc', 'input.nondetstates'
                , 'input.nondeterministic', 'input.alternating', 'exit_status', 'exit_code', 'output.ap', 'output.edges','output.transitions',
                'output.nondetstates', 'output.scc', 'output.nondeterministic', 'output.alternating'])
    """
    # sum filtered columns
    sum_filtered_columns = csv_file.sum(axis=0)
    df = pd.DataFrame(sum_filtered_columns)
    return df
    print(df.at['output.acc_sets', 0], np.round((df.at['time', 0]), 3))
    return df.at['output.acc_sets', 0], np.round((df.at['time', 0]), 3)



def add_input(data_frame, dict):
    dict["Acceptance sets"].append(data_frame.at['input.acc_sets', 0])
    dict["% reduction"].append(0)
    dict["Time"].append(0)

def add_output(data_frame, dict):
    intput_sets = data_frame.at['input.acc_sets', 0]
    output_sets = data_frame.at['output.acc_sets', 0]
    dict["Acceptance sets"].append(output_sets)
    dict["% reduction"].append(np.round(100*output_sets / intput_sets, 1) )
    dict["Time"].append(np.round((data_frame.at['time', 0]), 3))

def to_string(output, mrkdwn):
    if output is not None:
        f = open(output, m)
        f.write(mrkdwn)
        f.close()
    else:
        print(mrkdwn)



def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("-L1", "--level1", help="CSV file of statistics level1", default=None)
    parser.add_argument("-L2", "--level2", help="CSV file of statistics level1", default=None)
    parser.add_argument("-L3", "--level3", help="CSV file of statistics level1", default=None)
    parser.add_argument("-O", "--outfile", help="File to print output to.", default=None)

    args = parser.parse_args()

    if not (args.level1 or args.level2 or args.level3) :
        print("No statistics to process.", file=sys.stderr)

    dict = {"Acceptance sets" : [], "% reduction": [], "Time" : []}
    added_input = False
    indices = ['Input']

    if args.level1:
        level1 = parse_csv(args.level1)
        add_input(level1, dict)
        added_input = True
        add_output(level1, dict)
        indices.append("Level1")


    if args.level2:
        level2 = parse_csv(args.level2)
        if not added_input:
            add_input(level2, dict)
            added_input = True
        add_output(level2, dict)
        indices.append("Level2")

    if args.level3:
        level3 = parse_csv(args.level3)
        if not added_input:
            add_input(level3, dict)
            added_input = True
        add_output(level2, dict)
        indices.append("Level3")

    df = pd.DataFrame(dict,
                    index =indices)

    mrkdwn = df.to_markdown()
    print(mrkdwn)






if __name__ == "__main__":
    main(sys.argv[1:])
