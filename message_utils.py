import re
import emoji

def remove_emoji(message: str):
    return emoji.replace_emoji(message, replace='')
