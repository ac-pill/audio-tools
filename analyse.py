import os
import argparse
from pydub import AudioSegment

# Setup argument parser
parser = argparse.ArgumentParser(
    description="Convert audio files to a specified format with given bitrate and sample rate."
)
parser.add_argument(
    "-i", "--input_folder", type=str, required=True, help="Folder containing the audio files to be converted"
)

# Process each file in the directory
def process(file_path):
    audio = AudioSegment.from_file(file_path)
    print(f"Processing: {os.path.basename(file_path)}")
    print(f" - Channels: {audio.channels}")
    print(f" - Sample Rate: {audio.frame_rate} Hz")
    print(f" - Bit Width: {audio.sample_width * 8} bit")
    print(f" - Frame Width: {audio.frame_width} bytes per frame ({audio.sample_width * 8}-bit depth across {audio.channels} channels)")


def main():
    args = parser.parse_args()

    for root, dirs, files in os.walk(args.input_folder):
        for filename in files:
            if filename.lower().endswith((".wav", ".mp3")):
                file_path = os.path.join(root, filename)
                process(file_path)

if __name__ == "__main__":
    main()