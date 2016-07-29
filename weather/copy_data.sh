#!/bin/bash -ex
for i in "$@"
do
case $i in
    --config=*)
    CONFIG="${i#*=}"

    ;;
    --output=*)
    OUTPUT="${i#*=}/"
    #OUTPUTT="${i#*=}/temp2.txt"
    ;;
    *)
            # unknown option
    ;;
esac
done


files=/home/tsubic/workspace/wee_archie/data/bomex_dump_*nc


for f in `ls -v /home/tsubic/workspace/wee_archie/data2/*.nc`
do
cp $f $OUTPUT
done
