#!/bin/sh


#python3 ./csv_gen.py -F ./ltl3tela.hoa -L1 -L2 -L3 -G -O ./statistics/z3/inc

#python3 ./csv_gen.py -F ./ltl2tgba.hoa -L1 -L2 -L3 -G -O ./statistics/z3/inc

#python3 ./csv_gen.py -F ./rab4.hoa -L1 -L2 -L3 -G -O ./statistics/z3/inc

#autcross --file='./bp_sets/rab4.hoa' --tool='python3 ./main.py -F%H -O%O -L 1 -I' --language-preserved --csv='./statistics/z3/rab4.l1.csv' 


#autcross --file='./bp_sets/rab4.hoa' --tool='python3 ./main.py -F%H -O%O -L 2 -I' --language-preserved --csv='./statistics/z3/rab4.l2.csv'

#autcross --file='./bp_sets/rab4.hoa' --tool='python3 ./main.py -F%H -O%O -L 3 -I' --language-preserved --csv='./statistics/z3/rab4.l3.csv'

#autcross --file='./bp_sets/ltl3tela.hoa' --tool='python3 ./main.py -F%H -O%O -L 1 -I' --language-preserved --csv='./statistics/z3/ltl3tela.l1.csv'

#autcross --file='./bp_sets/ltl3tela.hoa' --tool='python3 ./main.py -F%H -O%O -L 2 -I' --language-preserved --csv='./statistics/z3/ltl3tela.l2.csv'

#autcross --file='./bp_sets/ltl3tela.hoa' --tool='python3 ./main.py -F%H -O%O -L 3 -I' --language-preserved --csv='./statistics/z3/ltl3tela.l3.csv'


#autcross --file='./bp_sets/ltl2tgba.hoa' --tool='python3 ./main.py -F%H -O%O -L 1 -I' --language-preserved --csv='./statistics/z3/ltl2tgba.l1.csv'

#autcross --file='./bp_sets/ltl2tgba.hoa' --tool='python3 ./main.py -F%H -O%O -L 2 -I' --language-preserved --csv='./statistics/z3/ltl2tgba.l2.csv'

autcross --file='./bp_sets/ltl2tgba.hoa' --tool='python3 ./main.py -F%H -O%O -L 3 -I -G' --language-preserved --csv='./statistics/z3/ltl2tgba.l3.csv'

