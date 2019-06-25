#!/bin/sh

KEYFINDER_CLI=keyfinder-cli/keyfinder-cli
BPM_TAG=bpm-tools-0.3/bpm-tag

$KEYFINDER_CLI -n openkey "$1" > "$1".meta
$BPM_TAG -n "$1" 2>&1 > /dev/null | awk -F ": " '{print $NF}' | cut -d ' ' -f 1 >> "$1".meta
