#!/usr/bin/env bash

set -e

SCRIPT_DIR=$(dirname "$0")
cd "$SCRIPT_DIR"

mkdir -p foo/bar

echo "first" > foo/first
echo "second" > foo/second
echo "third" > foo/third
echo "fourth and fifth" > "foo/fourth and fifth"
echo "😀" > foo/😀

echo "hidden" > foo/bar/hidden
echo ".hidden" > foo/bar/.hidden
