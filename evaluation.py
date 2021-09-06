#!/usr/bin/env/python3

import os
def eval(file_names):
    
    for name in file_names:
        a = "autcross --file=" + name + " --tool='python3 ./main.py -F%H -O%O -L 1' --language-preserved --csv='./optimized_stats/" + name +".tele.csv'" 
        b = "autcross --file=" + name + " --tool='python3 ./main.py -F%H -O%O -L 2' --language-preserved --csv='./optimized_stats/" + name +".scc.csv'"
        c = "autcross --file=" + name + " --tool='python3 ./main.py -F%H -O%O -L 3' --language-preserved --csv='./optimized_stats/" + name +".prec.csv'"
        d = "autcross --file=" + name + " --tool='python3 ./main.py -F%H -O%O -L 4' --language-preserved --csv='./optimized_stats/" + name +".cycles.csv'"
        
        os.system(a)
        os.system(b)
        os.system(c)
        os.system(d)


files = ["ltl2tgba.hoa", "ltl3tela.hoa", "rab4.hoa"]

eval(files)
