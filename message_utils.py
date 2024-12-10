import re
import emoji

def extract_jp_message(message: str):
    remove_blank_from_surfix = re.sub(r'\[ja\]\s*[:]\s*', '[ja] : ', message)
    remove_quotation_mark = re.sub(r"['\"]", '', remove_blank_from_surfix)

    cut_ja_str = re.search(r'\[ja\] : (.*)', remove_quotation_mark, re.DOTALL)

    if cut_ja_str:
        return cut_ja_str.group(1)
    else:
        return ""

def remove_emoji(message: str):
    return emoji.replace_emoji(message, replace='')
