#!/bin/bash
for i in $(ls -d */); do 
    cd $i;
    ./Autosort;
    cd ..;
    echo ${i%%/};
done
