#!/bin/sh



autcross --file='./bp_sets/ltl2tgba.hoa' --tool='python3 ./main.py -F%H -O%O -L 1' --language-preserved --csv='./statistics/level1/ltl2tgba.tele.csv'

autcross --file='./bp_sets/ltl3tela.hoa' --tool='python3 ./main.py -F%H -O%O -L 1' --language-preserved --csv='./statistics/level1/ltl3tela.tele.csv'


autcross --file='./bp_sets/rab4.hoa' --tool='python3 ./main.py -F%H -O%O -L 1' --language-preserved --csv='./statistics/level1/rab4.tele.csv'

