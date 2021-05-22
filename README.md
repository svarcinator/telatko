# telatko

Tool to simplify acceptance conditons of TELA automata.

Running TELAtko tool: python3 ./main.py -F myautomaton.hoa -O output
The overview of the options:
Switch -F -- path to input automaton.
Switch -O -- path to output file.
Switch -L --mode has options 1, 2, 3, 4. It sets level of simplification. If ommited, default level is 1.
Switch -T --timeout = number of seconds, that QBF solver solves the formula. If ommited, default timeout is 50 seconds.

