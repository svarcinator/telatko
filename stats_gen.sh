#!/bin/sh



autcross --file='./bp_sets/ltl2tgba.hoa' --tool='python3 ./main.py -F%H -O%O -L 2' --language-preserved --csv='./from_input_aut/ltl2tgba.scc.csv'

autcross --file='./bp_sets/ltl2tgba.hoa' --tool='python3 ./main.py -F%H -O%O -L 3' --language-preserved --csv='./from_input_aut/ltl2tgba.prec.csv'

autcross --file='./bp_sets/ltl2tgba.hoa' --tool='python3 ./main.py -F%H -O%O -L 4' --language-preserved --csv='./from_input_aut/ltl2tgba.cycles.csv'



autcross --file='./bp_sets/rab4.hoa' --tool='python3 ./main.py -F%H -O%O -L 2' --language-preserved --csv='./from_input_aut/rab4.scc.csv'

autcross --file='./bp_sets/rab4.hoa' --tool='python3 ./main.py -F%H -O%O -L 3' --language-preserved --csv='./from_input_aut/rab4.prec.csv'

autcross --file='./bp_sets/rab4.hoa' --tool='python3 ./main.py -F%H -O%O -L 4' --language-preserved --csv='./from_input_aut/rab4.cycles.csv'


autcross --file='./bp_sets/ltl3tela.hoa' --tool='python3 ./main.py -F%H -O%O -L 2' --language-preserved --csv='./from_input_aut/ltl3tela.scc.csv'

autcross --file='./bp_sets/ltl3tela.hoa' --tool='python3 ./main.py -F%H -O%O -L 3' --language-preserved --csv='./from_input_aut/ltl3tela.prec.csv'

autcross --file='./bp_sets/ltl3tela.hoa' --tool='python3 ./main.py -F%H -O%O -L 4' --language-preserved --csv='./from_input_aut/ltl3tela.cycles.csv'
