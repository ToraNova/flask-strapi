#!/bin/sh

for t in $(ls examples/*_test.py); do
	pytest $t -s;
	[ ! "$?" -eq 0 ] && exit 1;
done
exit 0;
