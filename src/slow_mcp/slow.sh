#!/bin/sh

for sec in $(seq 1 300); do
    sleep 1
    echo "$sec"
done
