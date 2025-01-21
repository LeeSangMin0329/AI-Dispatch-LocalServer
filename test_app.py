import requests
import time
from flask import Flask, request, jsonify
from threading import Thread
from message_utils import extract_jp_message, remove_emoji
from openai_controller import query_gpt

import db_manager
import prompt_introduction
from datetime import datetime

app = Flask(__name__)

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.form.get("message")

    if not str(user_input).strip():
        return jsonify({"response": ""}) 
    
    start = time.time()
    
    converstations = db_manager.get_conversations()
    converstations.insert(0, prompt_introduction.rule_message)
    converstations.insert(0, prompt_introduction.introduction_message)

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
    
    # thread = Thread(target=send_to_tts_server, args=(message_jp,))
    # thread.start()

    return jsonify({"response": message_jp})

def send_to_tts_server(message: str):
    print(f"jp message: {message}")
    try:
        url = str("http://127.0.0.1:50001/requset_message_form_outside")
        response = requests.post(url, data={'message': message})

        if response.status_code == 200:
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

#app.run(host="127.0.0.1", port="50003")
def main():
    while True:
        message = input("Enter message: ")
        test_route(message)

        if message is None:
            continue
        
        
main()
