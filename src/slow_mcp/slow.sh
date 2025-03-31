#!/bin/sh

for sec in $(seq 1 125); do
    sleep 1
    echo "$sec"
done
