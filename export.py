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
parser.add_argument(
    "-o", "--output_folder", type=str, required=True, help="Output folder for the converted audio files"
)
parser.add_argument(
    "-f",
    "--format",
    type=str,
    required=True,
    choices=["ogg", "m4a", "mp3"],
    help="Target audio format for the conversion",
)
parser.add_argument("-b", "--bitrate", type=str, help="Bitrate for the converted audio")
parser.add_argument(
    "-s", "--sample_rate", type=float, help="Sample rate (kHz) for the converted audio"
)


# Process each file in the directory
def process(file_path, input_folder, output_folder, sample_rate, format, bitrate):
    audio = AudioSegment.from_file(file_path)
    audio = audio.set_frame_rate(int(sample_rate * 1000))  # Convert sample rate

    # Generate export path
    relative_path = os.path.relpath(file_path, start=input_folder)
    if format == 'm4a':
        ffmpeg_format = 'mp4'  # Use 'mp4' format for FFmpeg command
        export_path = os.path.join(output_folder, os.path.splitext(relative_path)[0] + ".m4a")
    else:
        ffmpeg_format = format
        export_path = os.path.join(output_folder, os.path.splitext(relative_path)[0] + "." + format)

    os.makedirs(os.path.dirname(export_path), exist_ok=True)  # Ensure the output directory exists
    audio.export(export_path, format=ffmpeg_format, bitrate=bitrate)


def main():
    args = parser.parse_args()
    input_folder = args.input_folder
    output_folder = args.output_folder
    sample_rate = args.sample_rate
    format = args.format
    bitrate = args.bitrate

    for root, dirs, files in os.walk(args.input_folder):
        for filename in files:
            if filename.lower().endswith((".wav", ".mp3")):
                file_path = os.path.join(root, filename)
                process(file_path, input_folder, output_folder, sample_rate, format, bitrate)

if __name__ == "__main__":
    main()
