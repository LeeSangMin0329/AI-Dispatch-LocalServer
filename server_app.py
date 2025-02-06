import requests
import time
import asyncio
import random
from io import BytesIO
from quart import Quart, request, jsonify

import conversation_manager
from openai_controller import query_stt, translate_ja

app = Quart(__name__)
app.config['MAX_CONTENT_LENGTH'] = 25 * 1024 * 1024

last_request_chat_time = time.time()
is_suggest_random_topic = False

@app.route("/chat", methods=["POST"])
async def receive_text():
    form = await request.form
    user_input = form.get("message")
    required_translate = request.form.get("required_translate")

    if not str(user_input).strip():
        return jsonify({"response": ""}) 
    
    if required_translate == "True":
        user_input = translate_ja(user_input)

    message_jp = chat_to_tts_server(user_input)

    return jsonify({"response": message_jp})

@app.route("/chat_audio", methods=["POST"])
async def receive_audio():
    files = await request.files
    audio_file = files.get("message")

    if not audio_file:
        return jsonify({"response": ""})
        
    audio_buffer = BytesIO(audio_file.read())

    user_input = query_stt(audio_buffer, language="ja")

    if not user_input:
        return jsonify({"response": ""}) 

    print(f"user: {user_input}")

    message_jp = chat_to_tts_server(user_input)

    return jsonify({"response": message_jp})

def chat_to_tts_server(user_input: str):
    global last_request_chat_time
    global is_suggest_random_topic

    message_jp, face, motion, user_input_ko, message_ko, is_required_summary = conversation_manager.chat(user_input)
    
    send_to_tts_server(message_jp, face, motion, user_input_ko, message_ko)

    if is_required_summary:
        conversation_manager.request_summary()

    last_request_chat_time = time.time()
    is_suggest_random_topic = False

    return message_jp

def chat_to_tts_server_with_screenshot():
    message_jp, face, motion, user_input_ko, message_ko = conversation_manager.chat_with_screenshot()
    send_to_tts_server(message_jp, face, motion, user_input_ko, message_ko)

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

# region monitor when dosen't chat
async def monitor_last_chat():
    global last_request_chat_time
    global is_suggest_random_topic

    random_seconds = get_random_seconds()

    while True:
        await asyncio.sleep(60)

        if is_suggest_random_topic:
            continue

        elapsed = time.time() - last_request_chat_time

        if elapsed > random_seconds:
            is_suggest_random_topic = True
            random_seconds = get_random_seconds()
            print(f"fire to last time from {last_request_chat_time}")
            chat_to_tts_server_with_screenshot()
            
@app.before_serving
async def startup_monitor():
    loop = asyncio.get_event_loop()
    loop.create_task(monitor_last_chat())

def get_random_seconds():
    return random.randint(2, 10) * 60
# endregion

if __name__ == "__main__":
    conversation_manager.try_request_summary_from_timestamp()

    app.run(host="127.0.0.1", port="50003")
