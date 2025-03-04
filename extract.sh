#!/bin/sh

# TODO: move to env
BPM_TAG=bpm-tag
KEYFINDER_CLI=keyfinder-cli

# TODO: move to python methods
$BPM_TAG -nf "$1" 2>&1 /dev/null | grep "BPM" | tail -n 1 | awk -F ": " '{print $NF}' | cut -d ' ' -f 1 > "$1".meta
$KEYFINDER_CLI -n openkey "$1" >> "$1".meta
