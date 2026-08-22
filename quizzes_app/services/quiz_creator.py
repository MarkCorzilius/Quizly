import json
import os
import shutil
import tempfile
import time

import whisper
import yt_dlp
from google import genai
from yt_dlp.utils import DownloadError
import random

_model = None


def create_quiz(video_url):
    """Download the video's audio, transcribe it, and generate a quiz from the transcript."""

    audio_path = download_audio(video_url)
    text = transcribe_audio(audio_path)
    quiz_data = generate_quiz(text)

    return quiz_data


def download_audio(url):
    """Download the best available audio track from a URL to a temporary mp3 file."""

    if not shutil.which("ffmpeg"):
        raise ValueError("ffmpeg is not installed or not on PATH.")
    fd, output_path = tempfile.mkstemp(suffix=".mp3")
    os.close(fd)
    ydl_opts = {
    "format": "bestaudio/best",
    "outtmpl": output_path,
    "quiet": True,
    "noplaylist": True,
    "overwrites": True,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except DownloadError as error:
        raise ValueError(f"Could not download video: {error}")
    return output_path


def get_model():
    """Lazily load and cache the Whisper transcription model."""

    global _model
    if _model is None:
        _model = whisper.load_model("base")
    return _model


def transcribe_audio(audio_path):
    """Transcribe the audio file at the given path to plain text."""

    result = get_model().transcribe(audio_path)
    return result["text"]


client = genai.Client()


def generate_quiz(text):
    """Ask the Gemini model to build a 10-question JSON quiz from the transcript text."""

    interaction = client.interactions.create(
        model="gemini-3.6-flash",
        input=text,
        system_instruction="""
            Based on the following transcript, generate a quiz in valid JSON format.

            The quiz must follow this exact structure:
            {
                "title": "Create a concise quiz title based on the topic of the transcript.",
                "description": "Summarize the transcript in no more than 150 characters.",
                "questions": [
                    {
                        "question_title": "The question goes here.",
                        "question_options": [
                            "Option A",
                            "Option B",
                            "Option C",
                            "Option D"
                        ],
                        "answer": "The correct answer from the above options"
                    }
                ]
            }

            Requirements:
            - Exactly 10 questions.
            - Each question must have exactly 4 distinct answer options.
            - Only one correct answer is allowed per question.
            - The correct answer must be present in question_options.
            - Questions and answers must be based only on the transcript.
            - Do not invent information.
            - The description must not contain quiz questions or answers.
            - The output must be valid JSON and parsable with Python's json.loads().
            - Do not include explanations, comments, markdown, or any text outside the JSON.
        """
    )

    quiz_data = json.loads(interaction.output_text)
    for question in quiz_data.get("questions", []):
        random.shuffle(question["question_options"])
        
    return quiz_data