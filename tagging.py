import os
import argparse
import json
import librosa
import numpy as np

# Setup argument parser
parser = argparse.ArgumentParser(description="Tag audio files with tempo and key, and save the results to JSON.")
parser.add_argument("-i", "--input_folder", type=str, required=True, help="Folder containing the audio files to be tagged")
parser.add_argument("-o", "--output_folder", type=str, required=True, help="Output folder for the JSON files")
parser.add_argument("-n", "--filename", type=str, required=False, help="Optional single JSON filename to aggregate all tags")

def process(file_path, json_filename=None):
    # Show process
    print(f'Processing file: {file_path}')
    # Load the audio file
    y, sr = librosa.load(file_path, sr=None)

    # Extracting the tempo
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)

    # Extracting chroma features to infer the key
    chromagram = librosa.feature.chroma_cqt(y=y, sr=sr)
    chroma_mean = np.mean(chromagram, axis=1)

    # Assuming the key is major if the maximum chroma mean is in the first 12 bins, and minor if in the next 12.
    key_idx = np.argmax(chroma_mean)
    key_note = librosa.midi_to_note([key_idx % 12])[0]  # Getting the note name (C, C#, D, etc.)

    # Check if the note is a flat note and handle accordingly
    if 'b' in key_note:
        key_note = key_note[:-1]  # This keeps the flat notation but removes the octave number
    else:
        key_note = key_note[0]  # This keeps just the note letter

    key_type = 'major' if key_idx < 12 else 'minor'

    # Building the tags dictionary
    tags = {
        "Tempo": "{:.0f}".format(tempo),
        "Key": f"{key_note} {key_type}",
        "Mood": "",
        "Instruments": "",
        "Genre": "",
        "Location": "",
    }

    return os.path.basename(file_path), tags
    
def save_to_json(data, path, mode='w'):
    with open(path, mode) as f:
        json.dump(data, f, indent=4)

def main():
    args = parser.parse_args()

    if args.filename:
        output_path = os.path.join(args.output_folder, args.filename)
        if os.path.exists(output_path):
            print("Appending to existing JSON file.")
            mode = 'a'  # Append mode
        else:
            print("Creating new JSON file.")
            mode = 'w'  # Write mode
        aggregated_tags = {}

    for root, _, files in os.walk(args.input_folder):
        for filename in files:
            if filename.lower().endswith((".wav", ".mp3")):
                file_path = os.path.join(root, filename)
                basename, tags = process(file_path)

                if args.filename:
                    aggregated_tags[basename] = tags
                else:
                    individual_output_path = os.path.join(args.output_folder, f"{basename}.json")
                    save_to_json({basename: tags}, individual_output_path)
                    print(f"Saved tags for {basename} to {individual_output_path}")

    if args.filename:
        save_to_json(aggregated_tags, output_path, mode)
        print(f"Saved aggregated tags to {output_path}")

if __name__ == "__main__":
    main()