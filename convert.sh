#!/bin/bash
set -e

TARGET=$1

DIR=$(dirname $0)
FILES=$(find $TARGET -name *.tpl)

for f in $FILES; do
    echo $f
    python $DIR/upgrade.py < $f > /tmp/xx
    mv /tmp/xx $f
done

