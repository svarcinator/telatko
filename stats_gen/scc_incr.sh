#!/bin/sh

RAB=./../automata/rab4.hoa
LTL3TELA=./../automata/ltl3tela.hoa
LTL2TGBA=./../automata/ltl2tgba.hoa

CSV_FILE=./../statistics/new/scc_incr



autcross --file=$RAB --tool='python3 ./../telatko.py -F%H -O%O -L 1 -S -I' --language-preserved --csv=$CSV_FILE'/rab4.l1.csv' 


autcross --file=$RAB --tool='python3 ./../telatko.py -F%H -O%O -L 2 -S -I' --language-preserved --csv=$CSV_FILE'/rab4.l2.csv'

autcross --file=$RAB --tool='python3 ./../telatko.py -F%H -O%O -L 3 -S -I' --language-preserved --csv=$CSV_FILE'/rab4.l3.csv'

autcross --file=$RAB --tool='python3 ./../telatko.py -F%H -O%O -L 3 -G -S -I' --language-preserved --csv=$CSV_FILE'/rab4.g.csv'


autcross --file=$LTL3TELA --tool='python3 ./../telatko.py -F%H -O%O -L 1 -S -I' --language-preserved --csv=$CSV_FILE'/ltl3tela.l1.csv'

autcross --file=$LTL3TELA --tool='python3 ./../telatko.py -F%H -O%O -L 2 -S -I' --language-preserved --csv=$CSV_FILE'/ltl3tela.l2.csv'

autcross --file=$LTL3TELA --tool='python3 ./../telatko.py -F%H -O%O -L 3 -S -I' --language-preserved --csv=$CSV_FILE'/ltl3tela.l3.csv'
autcross --file=$LTL3TELA --tool='python3 ./../telatko.py -F%H -O%O -L 3 -G -S -I' --language-preserved --csv=$CSV_FILE'/ltl3tela.g.csv'



autcross --file=$LTL2TGBA --tool='python3 ./../telatko.py -F%H -O%O -L 1 -S -I' --language-preserved --csv=$CSV_FILE'/ltl2tgba.l1.csv'

autcross --file=$LTL2TGBA --tool='python3 ./../telatko.py -F%H -O%O -L 2 -S -I' --language-preserved --csv=$CSV_FILE'/ltl2tgba.l2.csv'

autcross --file=$LTL2TGBA --tool='python3 ./../telatko.py -F%H -O%O -L 3 -S -I' --language-preserved --csv=$CSV_FILE'/ltl2tgba.l3.csv'

autcross --file=$LTL2TGBA --tool='python3 ./../telatko.py -F%H -O%O -L 3 -G -S -I' --language-preserved --csv=$CSV_FILE'/ltl2tgba.g.csv'

