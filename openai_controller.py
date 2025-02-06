import io
import openai
import time
from message_utils import postprocess_stt, postprocess_llm_answer
from openai_key import API_KEY
from prompt_introduction import translation_rule_ko_message, translation_rule_ja_message
from screenshot_utils import get_screenshot_to_base64

MODEL_NAME = "ft:gpt-4o-2024-08-06:personal:yuki-multi:AwUHV1ml"

client = openai.OpenAI(api_key=API_KEY)

def query_gpt(messages: list) -> str:
    start = time.time()
    
    completion = client.chat.completions.create(
        model = MODEL_NAME,
        messages = messages
        )
    
    end = time.time()
    print(f"llm query time : {end - start}")

    answer = completion.choices[0].message.content

    return postprocess_llm_answer(answer)

def query_gpt_mini(messages: list) -> str:
    start = time.time()
    
    completion = client.chat.completions.create(
        model = "gpt-4o-mini",
        messages = messages
        )
    
    end = time.time()
    print(f"llm query time : {end - start}")

    answer = completion.choices[0].message.content

    return answer
    
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
    return result

def translate_ko(message: str):
    prompts = []

    prompts.append(translation_rule_ko_message)
    prompts.append({"role" : "user", "content" : message})

    result = query_gpt_mini(prompts)

    print(f"translate result: {result}")
    return result

def translate_ja(message: str) -> str:
    prompts = []

    prompts.append(translation_rule_ja_message)
    prompts.append({"role" : "user", "content" : message})

    result = query_gpt_mini(prompts)

    print(f"translate result: {result}")
    return result

def quary_with_screenshot(recent_messages: list, screenshot_message: str)-> str:
    screenshot = get_screenshot_to_base64()

    if not screenshot:
        print(f"screenshot is empty")
        return ""
    
    recent_messages.append({"role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": screenshot_message
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/png;base64,{screenshot}",
                                        "detail": "low"
                                        },
                                },
                            ]})
    
    return query_gpt(recent_messages)
