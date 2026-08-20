import yt_dlp
import whisper
from google import genai


def create_quiz(video_url):
    audio_path = download_audio(video_url)
    text = transcribe_audio(audio_path)
    quiz_data = generate_quiz(text)

    return quiz_data


def download_audio(url):
    output_path = "audio.mp3"
    ydl_opts = {
    "format": "bestaudio/best",
    "outtmpl": output_path,
    "quiet": True,
    "noplaylist": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])


model = whisper.load_model("turbo")

def transcribe_audio(audio_path):
    result = model.transcribe(audio_path)
    return result["text"]


client = genai.Client()

def generate_quiz(text):
    interaction = client.interactions.create(
        model="gemini-3.7-flash",
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

    return interaction.output_text