import librosa
import simpleaudio as sa
import numpy as np

def check_audio_file(file_path):
    try:
        # Load the audio file
        y, sr = librosa.load(file_path, sr=None)
        duration = librosa.get_duration(y=y, sr=sr)

        print(f"File: {file_path}")
        print(f"Sample Rate: {sr}")
        print(f"Duration: {duration} seconds")
        print("File loaded successfully!")

        # Play a short segment of the audio
        start_sample = 0  # Start at the beginning
        end_sample = int(sr * 5)  # Play for 5 seconds
        segment = y[start_sample:end_sample]
        
        # Convert the audio array to int16 format for playback
        segment_int16 = (segment * 32767).astype(np.int16)
        play_obj = sa.play_buffer(segment_int16, 1, 2, sr)
        play_obj.wait_done()

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    file_path = input("Enter the path to the audio file: ")
    check_audio_file(file_path)
