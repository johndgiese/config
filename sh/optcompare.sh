#!/bin/bash

for opt in 0 1 2 3; do
    gcc -S -O$opt -masm=intel -o opt$opt.s $@
done

gvim -O opt0.s opt1.s opt2.s opt3.s &
