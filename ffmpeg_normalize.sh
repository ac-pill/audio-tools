#!/bin/bash

# Usage: ./normalize_lufs.sh input_folder output_folder target_lufs
# Example: ./normalize_lufs.sh ./input ./output -14

INPUT_FOLDER="$1"
OUTPUT_FOLDER="$2"
TARGET_LUFS="$3"

# Check if input arguments are provided
if [ -z "$INPUT_FOLDER" ] || [ -z "$OUTPUT_FOLDER" ] || [ -z "$TARGET_LUFS" ]; then
    echo "Usage: $0 input_folder output_folder target_lufs"
    exit 1
fi

# Function to process a single file
process_file() {
    local input_file="$1"
    local output_file="$2"
    echo "Processing $input_file..."

    ffmpeg -i "$input_file" -af loudnorm=I="$TARGET_LUFS":TP=-1:LRA=11 -ar 44100 "$output_file"
}

# Export the process_file function to be used in parallel
export -f process_file
export TARGET_LUFS

# Find all WAV and MP3 files in the input directory, maintain the directory structure in the output
find "$INPUT_FOLDER" -type f \( -iname \*.wav -o -iname \*.mp3 \) | while read -r file; do
    # Construct the output file path
    relative_path="${file#$INPUT_FOLDER/}"
    output_file="$OUTPUT_FOLDER/$relative_path"
    output_dir=$(dirname "$output_file")

    # Create the output directory if it doesn't exist
    mkdir -p "$output_dir"

    # Process the file
    process_file "$file" "$output_file"
done

echo "Normalization process completed."
