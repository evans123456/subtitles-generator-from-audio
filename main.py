import os
import nltk
import speech_recognition as sr
from pydub import AudioSegment

# Download necessary NLTK data
nltk.download('punkt')

def transcribe_audio(audio_path):
    recognizer = sr.Recognizer()
    audio = AudioSegment.from_file(audio_path)

    # Parameters for chunking
    chunk_length_ms = 30000  # Chunk length set to 30 seconds

    # Split audio into chunks
    chunks = [audio[i:i + chunk_length_ms] for i in range(0, len(audio), chunk_length_ms)]

    whole_text = ""
    for i, chunk in enumerate(chunks):
        chunk_filename = f"chunk{i}.wav"
        chunk.export(chunk_filename, format="wav")

        with sr.AudioFile(chunk_filename) as source:
            try:
                audio_listened = recognizer.record(source)
                text = recognizer.recognize_google(audio_listened)
                whole_text += f"{text} "
            except sr.UnknownValueError:
                print(f"Could not understand chunk {i}")
            except sr.RequestError as e:
                print(f"Could not request results from Google Speech Recognition service for chunk {i}: {e}")

        os.remove(chunk_filename)

    return whole_text.strip()

def create_srt(transcription, output_path, word_duration=0.5):
    words = nltk.word_tokenize(transcription)
    srt_content = ""
    start_time = 0.0

    for i, word in enumerate(words):
        start_time_str = format_time(start_time)
        end_time_str = format_time(start_time + word_duration)
        srt_content += f"{i+1}\n{start_time_str} --> {end_time_str}\n{word}\n\n"
        start_time += word_duration

    with open(output_path, "w") as srt_file:
        srt_file.write(srt_content)

def format_time(seconds):
    ms = int((seconds % 1) * 1000)
    seconds = int(seconds)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    return f"{hours:02}:{minutes:02}:{seconds:02},{ms:03}"

if __name__ == "__main__":
    audio_path = "podcast.mp3"  # Replace with your audio file path
    transcription = transcribe_audio(audio_path)
    if transcription:
        create_srt(transcription, "output.srt")
        print("Transcription and SRT creation completed successfully.")
    else:
        print("Transcription failed. Please check the audio file and try again.")
