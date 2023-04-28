#!/bin/sh

NUM_LOOPS=$1
NUM_CONCURRENT=2 # constant

readarray -d ',' -t RECOS < $2
IFS=';' read -ra PARAMS <<< $3

OUTFOLDER=$4
PREFIX=$5
SLIM_FILE=$6
SELECTION_STRENGTH=$7

function run_slim(){
    echo slim -d reco=${RECOS[i]} -d N1=${PARAMS[0]} -d N2=${PARAMS[1]} \
        -d growth=${PARAMS[2]} -d T1=${PARAMS[3]} -d T2=${PARAMS[4]} \
        -d output=\"$OUTFOLDER\" -d mut=$SELECTION_STRENGTH $SLIM_FILE \
;}

for ((i=0; i<$NUM_LOOPS; i++))
do
    for ((j=0; j<$NUM_CONCURRENT; j++))
    do
        run_slim
        i=$((i+1))
    done
    wait
done