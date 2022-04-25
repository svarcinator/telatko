#!/bin/bash

declare -a tools=("rab4" "ltl3tela" "ltl2tgba")


declare -a locations=("./new/basic" "./new/scc" "./new/incr" "./new/scc_incr" )
#declare -a locations=("./new/basic" )
 
SCRIPT_NAME=./parse_statistics.py

# Iterate the string array using for loop
for tool in ${tools[@]}; do
    for location in ${locations[@]}; do
        $SCRIPT_NAME -L1 $location/$tool.l1.csv -L2 $location/$tool.l2.csv -L3 $location/$tool.l3.csv -G $location/$tool.g.csv -O $location/$tool'.mrkdwn'
    done
    
done

