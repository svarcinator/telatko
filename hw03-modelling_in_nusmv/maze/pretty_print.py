"""
This script can be easily used to pretty print the output of the nuXmv.

If the counter example is found it is transformed to csv table.
Otherwise the message 'Congrats no counter example found!' is printed.

Example usage:

nuXmv example.smv | python3 pretty_nuXmv.py > output.csv
"""

from itertools import dropwhile
from copy import deepcopy

import sys

def _get_counter_example_lines(lines):
    return list(dropwhile(lambda x: not x.startswith('-> State:'), map(lambda x: x.strip(), lines)))


def _get_state_changes(lines):
    state_changes = []
    changes = None
    for line in lines:
        if line.startswith('-> State:'):
            if changes is not None:
                state_changes.append(changes)
            step_counter = int(line.split('.')[1].split(' ')[0])
            changes = {'step_counter': step_counter - 1}
        elif line == '-- Loop starts here':
            pass
        else:
            split = line.split(' = ')
            lhs = split[0]
            rhs = None
            if split[1] == 'FALSE':
                rhs = 0
            elif split[1] == 'TRUE':
                rhs = 1
            elif split[1].isdigit():
                rhs = int(split[1])
            else:
                rhs = split[1]
            changes[lhs] = rhs
    return state_changes


def _get_states(state_changes):
    states = []
    state = {}
    for changes in state_changes:
        for key, val in changes.items():
            state[key] = val
        states.append(deepcopy(state))
    return states


def _export_to_csv(states):
    for key in states[0].keys():
        print(key, end='')
        for i in range(len(states)):
            print(f',{states[i][key]}', end='')
        print()

if __name__ == '__main__':
    all_lines = sys.stdin.readlines()

    if len(all_lines) == 0:
        print('nuXmv output was not provided at STDIN.')
        sys.exit(1)

    lines = _get_counter_example_lines(all_lines)

    if len(lines) == 0:
        print('Congrats no counter example found!')
        sys.exit(0)

    state_changes = _get_state_changes(lines)
    states = _get_states(state_changes)

    _export_to_csv(states)    

