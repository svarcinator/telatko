#!/bin/sh

RAB=./../automata/rab4.hoa
LTL3TELA=./../automata/ltl3tela.hoa
LTL2TGBA=./../automata/ltl2tgba.hoa

CSV_FILE=./../statistics/new/basic

TELATKO=./../telatko.py




autcross --file=$RAB --tool=$TELATKO' -F%H -O%O -L 1' --language-preserved --csv=$CSV_FILE'/rab4.l1.csv' 


autcross --file=$RAB --tool=$TELATKO' -F%H -O%O -L 2' --language-preserved --csv=$CSV_FILE'/rab4.l2.csv'

autcross --file=$RAB --tool=$TELATKO' -F%H -O%O -L 3' --language-preserved --csv=$CSV_FILE'/rab4.l3.csv'

autcross --file=$RAB --tool=$TELATKO' -F%H -O%O -L 3 -G' --language-preserved --csv=$CSV_FILE'/rab4.g.csv'


autcross --file=$LTL3TELA --tool=$TELATKO' -F%H -O%O -L 1 ' --language-preserved --csv=$CSV_FILE'/ltl3tela.l1.csv'

autcross --file=$LTL3TELA --tool=$TELATKO' -F%H -O%O -L 2' --language-preserved --csv=$CSV_FILE'/ltl3tela.l2.csv'

autcross --file=$LTL3TELA --tool=$TELATKO' -F%H -O%O -L 3' --language-preserved --csv=$CSV_FILE'/ltl3tela.l3.csv'

autcross --file=$LTL3TELA --tool=$TELATKO' -F%H -O%O -L 3 -G' --language-preserved --csv=$CSV_FILE'/ltl3tela.g.csv'



autcross --file=$LTL2TGBA --tool=$TELATKO' -F%H -O%O -L 1' --language-preserved --csv=$CSV_FILE'/ltl2tgba.l1.csv'

autcross --file=$LTL2TGBA --tool=$TELATKO' -F%H -O%O -L 2' --language-preserved --csv=$CSV_FILE'/ltl2tgba.l2.csv'

autcross --file=$LTL2TGBA --tool=$TELATKO' -F%H -O%O -L 3' --language-preserved --csv=$CSV_FILE'/ltl2tgba.l3.csv'

autcross --file=$LTL2TGBA --tool=$TELATKO' -F%H -O%O -L 3 -G' --language-preserved --csv=$CSV_FILE'/ltl2tgba.g.csv'

