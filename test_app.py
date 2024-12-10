import openai
import requests
import time
from flask import Flask, request, jsonify
from threading import Thread
from openai_key import API_KEY
from message_utils import extract_jp_message, remove_emoji

app = Flask(__name__)
client = openai.OpenAI(api_key=API_KEY)

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.form.get("message")

    if not str(user_input).strip():
        return jsonify({"response": ""}) 
    
    start = time.time()
    
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "友達のように話す言葉で短く簡潔に話す"},
            {"role": "system", "content": """
                日本語でのみ回答してください。外来語や英単語は、カタカナで読み方を変換して出力してください。
            """},
            {"role": "user", "content": user_input}
        ])
    
    end = time.time()
    print(f"connect time: {end - start}")
    
    response_content = completion.choices[0].message.content

    print(f"original text: {response_content}")

    message_jp = remove_emoji(response_content)
    thread = Thread(target=send_to_tts_server, args=(message_jp,))
    thread.start()

    return jsonify({"response": response_content})

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
    with app.test_request_context('/chat', method='POST', json={'message': message}):
        # 라우트 함수 호출
        response = chat()
        print(response.get_json()['response'])  # 응답 출력

app.run(host="127.0.0.1", port="50003")
# def main():
#     while True:
#         message = input("Enter message: ")

#         test_route(message)
        
# main()
