#!/bin/bash
TARGET=$1

DIR=$(dirname $0)
FILES=$(find $TARGET -name *.tpl)

for f in $FILES; do
    python $DIR/upgrade.py < $f > /tmp/xx
    mv /tmp/xx $f
    echo $f
done

