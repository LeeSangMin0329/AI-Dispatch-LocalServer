import openai
from openai_key import API_KEY

client = openai.OpenAI(api_key=API_KEY)

def query_gpt(messages: list) -> str:
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=messages
        )
    
    return completion.choices[0].message.content
    