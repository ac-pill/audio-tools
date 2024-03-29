import os
import argparse
from pydub import AudioSegment
from pydub.effects import normalize

# Setup argument parser
parser = argparse.ArgumentParser(
    description="Normalize audio files to a specified LUFS level."
)
parser.add_argument(
    "-i", "--input_folder", type=str, help="Folder containing the audio files to be normalized"
)
parser.add_argument("l", "lufs", type=float, help="Target LUFS level for normalization")
args = parser.parse_args()


# Function to normalize audio
def normalize_audio(file_path, target_lufs):
    # Load the audio file
    audio = AudioSegment.from_file(file_path)
    # Normalize the audio to the target LUFS
    normalized_audio = normalize(audio, headroom=target_lufs)
    return normalized_audio


def normalize(file_path, lufs):
    # Process each file in the directory
    normalized_audio = normalize_audio(file_path, lufs)
    # Save the normalized audio with "_normalized" suffix
    normalized_path = (
        os.path.splitext(file_path)[0] + "_normalized" + os.path.splitext(file_path)[1]
    )
    normalized_audio.export(normalized_path, format=os.path.splitext(file_path)[1][1:])


def main():
    args = parser.parse_args()
    folder = args.input_folder
    lufs = args.lufs

    for filename in os.listdir(folder):
        if filename.lower().endswith((".wav", ".mp3")):
            file_path = os.path.join(args.folder, filename)
            normalize(file_path, lufs)


if __name__ == "__main__":
    main()
