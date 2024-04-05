# Export audio pipeline
# Usage: python export.py -i infolder -o outfolder -f m4a -b 96k -s 44.1 -d 16 -es 1 -fd 2 -t 15 60 -n -c -l -23
# For SVS production - Soundraw: python export.py -i input/Raw/Azuki/Soundraw -o output/Azuki  -f m4a -b 96k -s 44.1 -d 16 -es 1 -fd 2 -n -l -23
# For SVS production - Suno: python export.py -i input/Raw/Azuki/Suno -o output/Azuki  -f m4a -b 96k -s 44.1 -d 16 -t 15 60 -fd 2 -n -l -23

import os
import argparse
import subprocess
import tempfile
import time

from pydub import AudioSegment
from pydub.effects import normalize, compress_dynamic_range
from pydub.silence import split_on_silence

# Setup argument parser
parser = argparse.ArgumentParser(
    description="Convert and process audio files with various effects."
)
parser.add_argument("-i", "--input_folder", type=str, required=True, help="Folder containing the audio files to be processed")
parser.add_argument("-o", "--output_folder", type=str, required=True, help="Output folder for the processed audio files")
parser.add_argument("-f", "--format", type=str, required=True, choices=["ogg", "m4a", "mp3"], help="Target audio format for the output")
parser.add_argument("-b", "--bitrate", type=str, required=True, help="Bitrate for the output audio")
parser.add_argument("-s", "--sample_rate", type=float, required=True, help="Sample rate (kHz) for the output audio")
parser.add_argument("-d", "--bit_depth", type=int, choices=[8, 16, 24, 32], help="Bit depth for the output audio")
parser.add_argument("-es", "--end_silence", type=int, help="Remove silence at the end of the track exceeding this duration (seconds)")
parser.add_argument("-fd", "--fade", type=int, help="Apply fade in and fade out of this duration (seconds)")
parser.add_argument("-t","--trim", nargs=2, type=int, metavar=('OFFSET', 'LENGTH'), help="Offset and length for trimming the track (seconds)")
parser.add_argument("-n","--normalize", action="store_true", help="Normalize the audio to peak amplitude")
parser.add_argument("-c","--compress", action="store_true", help="Compress the dynamic range of the audio")
parser.add_argument("-l","--lufs", type=int, help="Target LUFS for loudness normalization")

def fx_normalize_lufs(input_file, output_file, target_lufs):
    """Normalize audio file loudness to the specified LUFS."""
    cmd = [
        "ffmpeg",
        "-i", input_file,
        "-af", f"loudnorm=I={target_lufs}:TP=-1:LRA=11",
        "-ar", "44100",
        '-y',  # Overwrite output file if it exists
        output_file
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def fx_apply_ffmpeg_filters(input_file, output_file):
    """
    Apply FFmpeg filters to improve audio quality.
    This example uses a low-pass filter to reduce high-frequency harshness.
    """
    # Define the FFmpeg command with a low-pass filter at 15000Hz
    cmd = [
        'ffmpeg',
        '-i', input_file,
        '-af', 'lowpass=f=15000',
        '-y',  # Overwrite output file if it exists
        output_file
    ]

    # Execute the FFmpeg command
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def fx_compress_audio(audio):
    """Compress the dynamic range of an audio segment."""
    return compress_dynamic_range(audio)

def fx_trim_silence(audio, silence_threshold=1):
    """Trim silence from the end of an audio segment that exceeds a given threshold."""
    # Split track into chunks separated by silence
    chunks = split_on_silence(audio, silence_thresh=-50, min_silence_len=1000)
    if chunks:
        audio = chunks[0]  # Assuming the first chunk is the main audio
        for chunk in chunks[1:]:
            if len(chunk) <= silence_threshold * 1000:  # Add short chunks
                audio += chunk
            else:  # Stop adding chunks when a long silence is found
                break
    return audio


def fx_apply_fade(audio, fade_duration):
    """Apply a fade in and fade out to an audio segment."""
    return audio.fade_in(fade_duration * 1000).fade_out(fade_duration * 1000)


def fx_trim_track(audio, offset, length):
    """Trim an audio segment starting from 'offset' for 'length' duration."""
    end_point = offset + length
    if end_point > len(audio):
        print(f"Warning: The final music length after {offset} seconds offset is shorter than {length} seconds.")
        end_point = len(audio)  # Adjust end_point to the audio length to avoid IndexError
    return audio[offset * 1000:end_point * 1000]


# Process each file in the directory
def process(
    file_path,
    input_folder,
    output_folder,
    sample_rate,
    file_format,
    bitrate,
    bit_depth,
    end_silence,
    fade,
    trim,
    normalize_audio,
    compress_audio,
    lufs=None,
):
    # Start Timer
    start_time = time.time()

    audio = AudioSegment.from_file(file_path)
    print(f"Processing: {os.path.basename(file_path)}")
    print(f" - Channels: {audio.channels}")
    print(f" - Sample Rate: {audio.frame_rate} Hz")
    print(f" - Bit Width: {audio.sample_width * 8} bit")
    print(
        f" - Frame Width: {audio.frame_width} bytes per frame ({audio.sample_width * 8}-bit depth across {audio.channels} channels)"
    )

    # Apply new features based on arguments
    if end_silence:
        print(f'Cropping End Silence to: {end_silence}s')
        audio = fx_trim_silence(audio, end_silence)
    if trim:
        print(f'Trimming file to offset: {trim[0]}, length: {trim[1]}')
        audio = fx_trim_track(audio, trim[0], trim[1])
    if fade:
        print(f'Applying fade: {fade}s ')
        audio = fx_apply_fade(audio, fade)
    if normalize_audio:
        print(f'Normalizing track')
        audio = normalize(audio)
    if compress_audio:
        print(f'Compressing track')
        audio = fx_compress_audio(audio)

    # Create a temporary directory to hold the intermediate WAV file
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_wav_path = os.path.join(temp_dir, "temp.wav")
        # Define the path for the WAV files
        filtered_wav_path = os.path.join(temp_dir, "filtered.wav")
        normalized_wav_path = os.path.join(temp_dir, "normalized.wav")
        
        audio.export(temp_wav_path, format="wav")

        if lufs is not None:
            
            # Apply FFmpeg filters for audio improvement
            print(f'Applying low-pass filter')
            fx_apply_ffmpeg_filters(temp_wav_path, filtered_wav_path)

            print(f'Normalizing to LUFS: {lufs}')
            fx_normalize_lufs(temp_wav_path, normalized_wav_path, lufs)
            
            # Read the normalized WAV file
            audio = AudioSegment.from_file(normalized_wav_path)

    # Export final audio
    audio = audio.set_frame_rate(int(sample_rate * 1000))  # Convert sample rate
    if bit_depth:
        audio = audio.set_sample_width(bit_depth // 8)

    # Generate export path
    relative_path = os.path.relpath(file_path, start=input_folder)
    if file_format == "m4a":
        ffmpeg_format = "mp4"  # Use 'mp4' format for FFmpeg command
        export_path = os.path.join(
            output_folder, os.path.splitext(relative_path)[0] + ".m4a"
        )
    else:
        ffmpeg_format = file_format
        export_path = os.path.join(
            output_folder, os.path.splitext(relative_path)[0] + "." + file_format
        )

    os.makedirs(
        os.path.dirname(export_path), exist_ok=True
    )  # Ensure the output directory exists
    audio.export(export_path, format=ffmpeg_format, bitrate=bitrate)
    
    print(f"Exported: {os.path.basename(export_path)}")
    print(
        f" - Format: {file_format}, Bitrate: {bitrate}, Sample Rate: {sample_rate} kHz, Bit Depth: {bit_depth} bit"
    )
    # Time tracking
    end_time = time.time()  # End timing for this file
    processing_time = end_time - start_time
    print(f"File processed in {processing_time:.2f} seconds.\n")


def main():
    args = parser.parse_args()
    total_start_time = time.time()  # Start timing for the entire batch

    input_folder = args.input_folder
    output_folder = args.output_folder
    sample_rate = args.sample_rate
    file_format = args.format

    bitrate = args.bitrate
    if not bitrate.endswith("k"):
        bitrate += "k"

    bit_depth = args.bit_depth

    end_silence = args.end_silence
    fade = args.fade
    trim = args.trim
    normalize_flag = args.normalize
    compress_flag = args.compress
    lufs = args.lufs

    for root, dirs, files in os.walk(args.input_folder):
        for filename in files:
            if filename.lower().endswith((".wav", ".mp3")):
                file_path = os.path.join(root, filename)
                process(
                    file_path=file_path,
                    input_folder=input_folder,
                    output_folder=output_folder,
                    sample_rate=sample_rate,
                    file_format=file_format,
                    bitrate=bitrate,
                    bit_depth=bit_depth,
                    end_silence=end_silence,
                    fade=fade,
                    trim=trim,
                    normalize_audio=normalize_flag,
                    compress_audio=compress_flag,
                    lufs=lufs,
                )

    total_end_time = time.time()  # End timing for the entire batch
    total_processing_time = total_end_time - total_start_time
    print(f"Total processing time for all files: {total_processing_time:.2f} seconds.")


if __name__ == "__main__":
    main()
