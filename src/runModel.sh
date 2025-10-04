#! /bin/bash
export PYTHONHASHSEED=1
MODEL="$1"
GRAPH="$2"
python main.py $MODEL $GRAPH $@
