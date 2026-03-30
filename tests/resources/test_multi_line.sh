#! /bin/bash

echo a a
echo b \
    b
echo \
    c \
    c
echo \
    d \
    d \
    d

declare \
    a=1

echo pipe test aaa | \
	sed 's/a/b/g' \
	| sed 's/b/c/g' \

[[ 1 -eq 1 ]] &&
	echo yes ||
	echo non

[[
	1 -eq 1
]] && echo yes
