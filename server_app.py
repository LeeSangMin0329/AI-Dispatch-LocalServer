import requests
import base64
from io import BytesIO
from flask import Flask, request, jsonify
from message_utils import remove_emoji
from openai_controller import query_gpt, query_stt, translate_ja
from translate_util import translate_conversation

import db_manager
import prompt_introduction
from datetime import datetime

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 25 * 1024 * 1024

@app.route("/chat", methods=["POST"])
def receive_text():
    user_input = request.form.get("message")
    required_translate = request.form.get("required_translate")

    if not str(user_input).strip():
        return jsonify({"response": ""}) 
    
    if required_translate == "True":
        user_input = translate_ja(user_input)

    message_jp = chat(user_input)

    return jsonify({"response": message_jp})

@app.route("/chat_audio", methods=["POST"])
def receive_audio():
    audio_file = request.files.get("message")

    if not audio_file:
        return jsonify({"response": ""})
        
    audio_buffer = BytesIO(audio_file.read())

    user_input = query_stt(audio_buffer, language="ja")

    if not user_input:
        return jsonify({"response": ""}) 

    print(f"user: {user_input}")

    message_jp = chat(user_input)

    return jsonify({"response": message_jp})

def chat(user_input: str):
    converstations = db_manager.get_conversations()
    converstations.insert(0, prompt_introduction.rule_message_jp)
    converstations.insert(0, prompt_introduction.introduction_message_jp)

    current_time = datetime.now()
    timestamp = current_time.strftime(f"%Y-%m-%d %H:%M:%S")
    converstations.append({"role" : "system", "content" : f"現在時刻 : {timestamp}"})
    converstations.append({"role" : "user", "content" : user_input})

    response_content = query_gpt(converstations)
    
    face, motion, answer = db_manager.split_message(response_content)
    message_jp = remove_emoji(answer)
    
    print(response_content)
    print(message_jp)

    db_manager.add_converstaion("user", user_input)
    db_manager.add_converstaion("assistant", message_jp, face, motion)

    user_input_ko, message_ko = translate_conversation(user_input, message_jp)
    
    send_to_tts_server(message_jp, face, motion, user_input_ko, message_ko)

    return message_jp

def send_to_tts_server(message: str, face: str, motion: str, log_user: str, log_answer: str):
    print(f"send message: {message}")
    try:
        url = str("http://127.0.0.1:50000/generate_audio")
        response = requests.post(url, data={'message': message, 'face': face, 'anim': motion, 'log_user': log_user, 'log_answer': log_answer})

        if response.status_code == 200:
            pass
        elif response.status_code == 202:
            pass
        else:
            print(f"TTS server failed with status code: {response.status_code}")
    except Exception as e:
        print(f"Error occurred when sending to TTS server: {str(e)}")

def test_route(message: str):
    with app.test_request_context('/chat', method='POST', data={'message': message, "required_translate" : "True"}):
        # 라우트 함수 호출
        response = receive_text()
        print(response.get_json()['response'])  # 응답 출력

app.run(host="127.0.0.1", port="50003")

# def main():
#     while True:
#         message = input("Enter message: ")
#         test_route(message)

#         if message is None:
#             continue
        
        
# main()
