# telatko  

Tool to simplify acceptance conditons of TELA.

Running TELAtko tool: ./telatko.py -F myautomaton.hoa 
The overview of the options:
Switch -F -- path to input automaton.  
Switch -O -- path to output file.  
Switch -L -- sets level of simplification [1, 2, 3].  
Switch -T -- timeout = number of seconds, that QBF solver solves the formula. If ommited, default timeout is 50 seconds.  
Switch -C -- minimizes number of clauses.  
Switch -I -- switches on the incremental solving.  
Switch -G -- switches on gradual solving.
Switch -O -- output_file.hoa  

Default:  
-G -I -L 3 -T 50
