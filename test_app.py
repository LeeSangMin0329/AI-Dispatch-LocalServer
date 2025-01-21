import requests
import time
import base64
from io import BytesIO
from flask import Flask, request, jsonify
from threading import Thread
from message_utils import extract_jp_message, remove_emoji
from openai_controller import query_gpt, query_stt

import db_manager
import prompt_introduction
from datetime import datetime

app = Flask(__name__)

@app.route("/chat", methods=["POST"])
def receive_text():
    user_input = request.form.get("message")

    if not str(user_input).strip():
        return jsonify({"response": ""}) 
    
    message_jp = chat(user_input)

    return jsonify({"response": message_jp})

@app.route("/chat_audio", methods=["POST"])
def receive_audio():
    audio = request.form.get("message")

    decoded_data = base64.b64decode(audio)

    audio_buffer = BytesIO(decoded_data)

    user_input = query_stt(audio_buffer, language="ja")

    if not user_input:
        return

    print(f"user: {user_input}")

    message_jp = chat(user_input)

    return jsonify({"response": message_jp})

def chat(user_input: str):
    start = time.time()
    
    converstations = db_manager.get_conversations()
    converstations.insert(0, prompt_introduction.rule_message_jp)
    converstations.insert(0, prompt_introduction.introduction_message_jp)

    current_time = datetime.now()
    timestamp = current_time.strftime(f"%Y-%m-%d %H:%M:%S")
    converstations.append({"role" : "system", "content" : f"현재 시간 : {timestamp}"})
    converstations.append({"role" : "user", "content" : user_input})

    response_content = query_gpt(converstations)
    
    end = time.time()
    print(f"connect time: {end - start}")

    print(response_content)

    face, motion, answer = db_manager.split_message(response_content)
    message_jp = remove_emoji(answer)

    db_manager.add_converstaion("user", user_input)
    db_manager.add_converstaion("assistant", message_jp, face, motion)
    
    thread = Thread(target=send_to_tts_server, args=(message_jp, face, motion))
    thread.start()

    return message_jp

def send_to_tts_server(message: str, face: str, motion: str):
    print(f"jp message: {message}")
    try:
        url = str("http://127.0.0.1:50000/generate_audio")
        response = requests.post(url, data={'message': message, 'face': face, 'anim': motion})

        if response.status_code == 200:
            pass
        elif response.status_code == 202:
            pass
        else:
            print(f"TTS server failed with status code: {response.status_code}")
    except Exception as e:
        print(f"Error occurred when sending to TTS server: {str(e)}")

def test_route(message: str):
    with app.test_request_context('/chat', method='POST', data={'message': message}):
        # 라우트 함수 호출
        response = chat()
        print(response.get_json()['response'])  # 응답 출력

app.run(host="127.0.0.1", port="50003")
# def main():
#     while True:
#         message = input("Enter message: ")
#         test_route(message)

#         if message is None:
#             continue
        
        
# main()
