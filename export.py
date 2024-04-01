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
parser.add_argument("-b", "--bitrate", type=str, required=True, help="Bitrate for the converted audio")
parser.add_argument(
    "-s", "--sample_rate", type=float, required=True, help="Sample rate (kHz) for the converted audio"
)
parser.add_argument("-d", "--bit_depth", type=int, choices=[8, 16, 24, 32], help="Bit depth for the converted audio")


# Process each file in the directory
def process(file_path, input_folder, output_folder, sample_rate, file_format, bitrate, bit_depth):
    audio = AudioSegment.from_file(file_path)
    print(f"Processing: {os.path.basename(file_path)}")
    print(f" - Channels: {audio.channels}")
    print(f" - Sample Rate: {audio.frame_rate} Hz")
    print(f" - Bit Width: {audio.sample_width * 8} bit")
    print(f" - Frame Width: {audio.frame_width} bytes per frame ({audio.sample_width * 8}-bit depth across {audio.channels} channels)")

    audio = audio.set_frame_rate(int(sample_rate * 1000))  # Convert sample rate
    if bit_depth:
        audio = audio.set_sample_width(bit_depth // 8)

    # IF we want Fade In and Out
    # 2 sec fade in, 3 sec fade out
    # faded = audio.fade_in(2000).fade_out(3000)

    # Generate export path
    relative_path = os.path.relpath(file_path, start=input_folder)
    if file_format == 'm4a':
        ffmpeg_format = 'mp4'  # Use 'mp4' format for FFmpeg command
        export_path = os.path.join(output_folder, os.path.splitext(relative_path)[0] + ".m4a")
    else:
        ffmpeg_format = file_format
        export_path = os.path.join(output_folder, os.path.splitext(relative_path)[0] + "." + file_format)

    os.makedirs(os.path.dirname(export_path), exist_ok=True)  # Ensure the output directory exists
    audio.export(export_path, format=ffmpeg_format, bitrate=bitrate)
    print(f"Exported: {os.path.basename(export_path)}")
    print(f" - Format: {file_format}, Bitrate: {bitrate}, Sample Rate: {sample_rate} kHz, Bit Depth: {bit_depth} bit\n")


def main():
    args = parser.parse_args()
    input_folder = args.input_folder
    output_folder = args.output_folder
    sample_rate = args.sample_rate
    file_format = args.format

    bitrate = args.bitrate
    if not bitrate.endswith('k'):
        bitrate += 'k'

    bit_depth = args.bit_depth

    for root, dirs, files in os.walk(args.input_folder):
        for filename in files:
            if filename.lower().endswith((".wav", ".mp3")):
                file_path = os.path.join(root, filename)
                process(file_path, input_folder, output_folder, sample_rate, file_format, bitrate, bit_depth)

if __name__ == "__main__":
    main()
