#!/usr/bin/env python3

import spot
import os
import sys

def main(argv):
    print("Current telatko z3 version - patterns ltl2tgba_det")
    telatko = "/home/xschwar3/telatko/telatko.py"

    os.environ['SPOT_TMPDIR'] = './autcross'
    os.environ['SPOT_TMPKEEP'] = '1'
    patterns_path = './'
    tools_order = [ 'ltl2tgba_det']
    for tool in tools_order:
        print(tool)
        os.system(f"autcross --no-checks --csv=patterns-telatko-{tool}.csv -F {patterns_path}/patterns-{tool}.hoa 'autfilt %H > %O' '{telatko} -F %H -T 30 -L 1 -I -O %O' '{telatko} -F %H -T 30 -L 2 -I -O %O' '{telatko} -F %H -T 30 -L 3 -I -O %O' '{telatko} -F %H -T 30 -L 3 -I -G -O %O' > autcross/{tool}.log 2>&1")


if __name__ == "__main__":
    main(sys.argv[1:])
