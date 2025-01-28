import numpy as np
import io
import openai
import time
from openai_key import API_KEY
from prompt_introduction import translation_rule_ko_message, translation_rule_ja_message

remove_words = ["ご視聴ありがとうござ", "by", "チョ", "トミ", "お疲れさまでした", "字幕視聴", "コメント欄に書いてあげてね", "咳 ごちそうさまでした", "【", "】", "パチパチパチ"]

client = openai.OpenAI(api_key=API_KEY)

def query_gpt(messages: list) -> str:
    start = time.time()
    
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=messages
        )
    
    end = time.time()
    print(f"llm query time : {end - start}")
    
    return completion.choices[0].message.content
    
def query_stt(audio: io.BytesIO, language="ja") -> str:
    start = time.time()

    file_path = "./temp/temp_audio.mp3"
    with open(file_path, "wb") as f:
        f.write(audio.read())

    transcription = client.audio.transcriptions.create(
        model="whisper-1",
        file=open(file_path, "rb"),
        language=language,
        response_format="text"
    )

    result = postprocess_stt(transcription)

    end = time.time()
    print(f"whisper query time : {end - start}")
    return result.strip()

def postprocess_stt(transcription: str) -> str:
    if len(transcription) < 4:
        return ""

    for bad_word in remove_words:
        if bad_word in transcription:
            return ""
        
    return transcription

def translate_ko(message: str):
    prompts = []

    prompts.append(translation_rule_ko_message)
    prompts.append({"role" : "user", "content" : message})

    result = query_gpt(prompts)

    print(f"translate result: {result}")
    return result

def translate_ja(message: str) -> str:
    prompts = []

    prompts.append(translation_rule_ja_message)
    prompts.append({"role" : "user", "content" : message})

    result = query_gpt(prompts)

    print(f"translate result: {result}")
    return result