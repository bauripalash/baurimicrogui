#!/bin/sh

SOURCE_DIR="baurimicrogui"
OUTPUT_DIR="dist/baurimicrogui"
ARCH="xtensawin"

echo "[+] Compiling '$SOURCE_DIR'"

if [ ! -d "$SOURCE_DIR" ]; then
	echo "[X] SOURCE directory not found"
	exit 1
fi

mkdir -p "$OUTPUT_DIR"

find "$SOURCE_DIR" -type f -name "*.py" | while IFS= read -r file; do
	rel_path="${file#$SOURCE_DIR/}"
	target_dir="$OUTPUT_DIR/$(dirname "$rel_path")"
	mkdir -p "$target_dir"
	target_file="$target_dir/$(basename "$file" .py).mpy"
	if [ ! -f "$target_file" ] || [ "$file" -nt "$target_file" ]; then
		echo "> Compiling '$file' to '$target_file'"
		mpy-cross -march="$ARCH" "$file" -o "$target_file"
	else
		echo ">> Skipping '$file'. No changes are detected."
	fi

done

echo "[+] Finished Compiling"
