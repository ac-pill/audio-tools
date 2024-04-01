#!/bin/bash

# Usage: ./normalize_lufs.sh input_folder output_folder target_lufs
# Example: ./normalize_lufs.sh ./input ./output -14
# set -x  # Enable debugging

INPUT_FOLDER="${1%/}"
OUTPUT_FOLDER="${2%/}"
TARGET_LUFS="$3"

echo "Starting Normalization"
echo "$INPUT_FOLDER"
echo "$OUTPUT_FOLDER"
echo "$TARGET_LUFS"

# Check if input arguments are provided
if [ -z "$INPUT_FOLDER" ] || [ -z "$OUTPUT_FOLDER" ] || [ -z "$TARGET_LUFS" ]; then
    echo "Usage: $0 input_folder output_folder target_lufs"
    exit 1
fi

# Create the output directory if it doesn't exist
mkdir -p "$OUTPUT_FOLDER"

# Function to process a single file
process_file() {
    local input_file="$1"
    local output_file="$2"
    echo "Processing \"$input_file\"..."

    # Debugging: Echo the ffmpeg command to be executed
    echo ffmpeg -i \""$input_file"\" -af loudnorm=I="$TARGET_LUFS":TP=-1:LRA=11 -ar 44100 \""$output_file"\"

    (ffmpeg -i "$input_file" -af loudnorm=I="$TARGET_LUFS":TP=-1:LRA=11 -ar 44100 "$output_file" > /dev/null 2>&1)
    IFS=$' \t\n';
};

# Export the process_file function to be used in parallel
# export -f process_file
# export TARGET_LUFS

# Explicitly set IFS to empty for the read command and reset it within the loop
shopt -s nullglob
for fileName in "$INPUT_FOLDER"/*.{wav,mp3}; do
    if [ -f "$fileName" ]; then  # Check if it's a file
        # Construct the output file path
        only_name="${fileName#$INPUT_FOLDER/}"
        output_file="$OUTPUT_FOLDER/$only_name"

        echo "Filename: $fileName"
        echo "Basename: $only_name"
        echo "Output file: $output_file"

        # Process the file
        process_file "$fileName" "$output_file"
    fi
done 

unset fileName;

echo "Normalization process completed."
