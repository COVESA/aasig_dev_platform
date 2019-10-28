#!/bin/sh -e

cd "$(dirname "$0")"
export AASIGDP_TARGET=hikey960
./build.sh

