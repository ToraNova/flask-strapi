#!/bin/sh

tests=(\
	examples/a.py\
);
for t in ${tests[@]}; do
	pytest $t -s;
	[ "$?" -eq 1 ] && exit 1;
done
exit 0;
