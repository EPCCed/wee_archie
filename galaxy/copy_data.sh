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


files=/Users/ggibb2/Projects/Demos/wee_archie/galaxy/data/data*nc

for f in $files
do 
cp $f $OUTPUT
sleep 2
done
