#!/bin/sh


autcross --file='./bp_sets/ltl2tgba.hoa' --tool='python3 ./main.py -F%H -O%O -L 1' --language-preserved --csv='./increasing_level/ltl2tgba.tele.csv'

autcross --file='./bp_sets/ltl2tgba.hoa' --tool='python3 ./main.py -F%H -O%O -L 2' --language-preserved --csv='./increasing_level/ltl2tgba.scc.csv'

autcross --file='./bp_sets/ltl2tgba.hoa' --tool='python3 ./main.py -F%H -O%O -L 3' --language-preserved --csv='./increasing_level/ltl2tgba.prec.csv'

autcross --file='./bp_sets/ltl2tgba.hoa' --tool='python3 ./main.py -F%H -O%O -L 4' --language-preserved --csv='./increasing_level/ltl2tgba.cycles.csv'


autcross --file='./bp_sets/rab4.hoa' --tool='python3 ./main.py -F%H -O%O -L 1' --language-preserved --csv='./increasing_level/rab4.tele.csv'

autcross --file='./bp_sets/rab4.hoa' --tool='python3 ./main.py -F%H -O%O -L 2' --language-preserved --csv='./increasing_level/rab4.scc.csv'

autcross --file='./bp_sets/rab4.hoa' --tool='python3 ./main.py -F%H -O%O -L 3' --language-preserved --csv='./increasing_level/rab4.prec.csv'

autcross --file='./bp_sets/rab4.hoa' --tool='python3 ./main.py -F%H -O%O -L 4' --language-preserved --csv='./increasing_level/rab4.cycles.csv'
