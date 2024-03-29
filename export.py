import os
import argparse
from pydub import AudioSegment

# Setup argument parser
parser = argparse.ArgumentParser(
    description="Convert audio files to a specified format with given bitrate and sample rate."
)
parser.add_argument(
    "i", "folder", type=str, help="Folder containing the audio files to be converted"
)
parser.add_argument(
    "f",
    "format",
    type=str,
    choices=["ogg", "aac", "mp3"],
    help="Target audio format for the conversion",
)
parser.add_argument("b", "bitrate", type=str, help="Bitrate for the converted audio")
parser.add_argument(
    "s", "sample_rate", type=int, help="Sample rate (kHz) for the converted audio"
)


# Process each file in the directory
def process(file_path, sample_rate, format, bitrate):
    audio = AudioSegment.from_file(file_path)
    # Convert sample rate
    audio = audio.set_frame_rate(sample_rate * 1000)
    # Export the audio with the specified format and bitrate
    export_path = os.path.splitext(file_path)[0] + "." + format
    audio.export(export_path, format=format, bitrate=bitrate)


def main():
    args = parser.parse_args()
    folder = args.folder
    sample_rate = args.sample_rate
    format = args.format
    bitrate = args.bitrate

    for filename in os.listdir(folder):
        if filename.lower().endswith((".wav", ".mp3")):
            file_path = os.path.join(args.folder, filename)
            process(file_path, sample_rate, format, bitrate)


if __name__ == "__main__":
    main()
