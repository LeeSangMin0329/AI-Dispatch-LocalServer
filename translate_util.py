from openai_controller import translate_ko

def translate_conversation(user_input: str, message_jp: str):

    target_text = f"{user_input}|{message_jp}"
    translate_result = translate_ko(target_text)

    split_result = translate_result.split("|")

    if len(split_result) < 2:
        return "", split_result[0]
    
    return split_result[0], split_result[1]