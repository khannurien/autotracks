#!/bin/sh

if grep docker /proc/1/cgroup -qa; then
    KEYFINDER_CLI=keyfinder-cli
    BPM_TAG=bpm-tag
else
    KEYFINDER_CLI=keyfinder-cli/keyfinder-cli
    BPM_TAG=bpm-tools-0.3/bpm-tag
fi

$KEYFINDER_CLI -n openkey "$1" > "$1".meta
$BPM_TAG -nf "$1" 2>&1 /dev/null | grep "BPM" | tail -n 1 | awk -F ": " '{print $NF}' | cut -d ' ' -f 1 >> "$1".meta
