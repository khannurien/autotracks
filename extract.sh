#!/bin/sh

keyfinder-cli/keyfinder-cli -n openkey "$1" > "$1".meta
bpm-tools-0.3/bpm-tag -n "$1" 2>&1 > /dev/null | awk -F ": " '{print $NF}' | cut -d ' ' -f 1 >> "$1".meta
