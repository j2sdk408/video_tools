#!/usr/bin/env bash
# $1: file to be stripped

OUTPUT=`basename ${1}`

#dd bs=120 skip=1 if=${1} of=${OUTPUT}

dd if=${1} bs=512k | { dd bs=120 count=1 of=/dev/null; dd bs=512k of=${OUTPUT}; }
