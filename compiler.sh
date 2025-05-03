#!/bin/sh

SOURCE_DIR="baurimicrogui"
OUTPUT_DIR="dist"

if [! -d "$SOURCE_DIR"]; then
	echo "SOURCE directory not found"
	exit 1
fi

mkdir -p "$OUTPUT_DIR"

