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


for f in `ls -v /home/tsubic/workspace/weather/data100/*.nc`
do
cp $f $OUTPUT
done
