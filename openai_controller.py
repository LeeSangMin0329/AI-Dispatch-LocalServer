import numpy as np
import io
import openai
from openai_key import API_KEY

client = openai.OpenAI(api_key=API_KEY)

def query_gpt(messages: list) -> str:
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=messages
        )
    
    return completion.choices[0].message.content
    
def query_stt(audio: io.BytesIO, language="ja") -> str:
    file_path = "./temp/temp_audio.mp3"
    with open(file_path, "wb") as f:
        f.write(audio.read())

    transcription = client.audio.transcriptions.create(
        model="whisper-1",
        file=open(file_path, "rb"),
        language=language,
        response_format="text"
    )
    return transcription.strip()