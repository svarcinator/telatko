#!/bin/sh



autcross --file='./bp_sets/ltl2tgba.hoa' --tool='python3 ./main.py -F%H -O%O -L 2' --language-preserved --csv='./statistics/optimized_l2/ltl2tgba.scc.csv'





autcross --file='./bp_sets/rab4.hoa' --tool='python3 ./main.py -F%H -O%O -L 2' --language-preserved --csv='./statistics/optimized_l2/rab4.scc.csv'


autcross --file='./bp_sets/ltl3tela.hoa' --tool='python3 ./main.py -F%H -O%O -L 2' --language-preserved --csv='./statistics/optimized_l2/ltl3tela.scc.csv'


