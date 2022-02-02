#!/bin/sh



autcross --file='./union.ltl3tela.l1' --tool='python3 ./print_aut.py -F%H -O%O' --language-preserved --csv='./statistics/union.ltl3tela.l1.csv'

autcross --file='./union.ltl3tela.l2' --tool='python3 ./print_aut.py -F%H -O%O' --language-preserved --csv='./statistics/union.ltl3tela.l2.csv'

autcross --file='./union.ltl3tela.l3' --tool='python3 ./print_aut.py -F%H -O%O' --language-preserved --csv='./statistics/union.ltl3tela.l3.csv'


