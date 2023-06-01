import spot
import os
import re
from ltlcross_runner import LtlcrossRunner, ResultsAnalyzer
import sys

def main(argv):
    tools = {
    'ltl2tgba_det': 'ltl2tgba -D -G %f > %O ',
    'ltl3tela_det': '/home/xschwar3/ltl3tela-master/ltl3tela  -D1 -f %f > %O',
    'ltl2tgba': 'ltl2tgba %f > %O ',
    'ltl3tela': '/home/xschwar3/ltl3tela-master/ltl3tela -f %f > %O',
    'delag': '/home/xschwar3/owl/bin/owl ltl2dela -f %f > %O',
    'rabinizer4': '/home/xschwar3/owl/bin/owl ltl2dgra -f %f > %O',
    }

    tools_order = [ 'ltl2tgba_det']

    rand_ltl = 'patterns.ltl'
    rand_aut = 'patterns.csv'
    lcr = LtlcrossRunner(tools, formulas = [rand_ltl], res_filename = rand_aut)
    lcr.run_ltlcross(automata = True, timeout = '60')
    ra = ResultsAnalyzer(rand_aut)
    ra.parse_results()
    ltlf_translated = {}

    for tool in tools_order:
        fs = ra.values.filter(items = [('acc', tool)]).dropna()

        ltlf_translated[tool] = len(fs[fs[('acc', tool)] > 1])

        fd = open('random-' + tool + '.hoa', 'w')
        for (ix, _), _ in fs.iterrows():
            fd.write(ra.aut_for_id(ix, tool).to_str() + '\n')
        fd.close()

if __name__ == "__main__":
    main(sys.argv[1:])
