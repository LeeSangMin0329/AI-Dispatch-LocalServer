import json
from typing import List

class Prompt_memory:
    def __init__(self, file_path: str = "chat_history.json"):
        self.file_path = file_path
        self.history = []  # Stores the chat history as a list of dictionaries

    def add_message(self, sender: str, message: str):
        """
        Add a new message to the chat history.
        """
        self.history.append({"role": sender, "message": message})

    def save_to_file(self):
        """
        Save the chat history to a JSON file.
        """
        try:
            with open(self.file_path, "w", encoding = "utf-8") as file:
                json.dump(self.history, file, ensure_ascii = False, indent = 4)
        except IOError as e:
            print(f"Error saving to file: {e}")

    def load_from_file(self):
        """
        Load the chat history from a JSON file.
        """
        try:
            with open(self.file_path, "r", encoding="utf-8") as file:
                self.history = json.load(file)
        except (IOError, json.JSONDecodeError) as e:
            print(f"Error loading from file: {e}")
            self.history = []

    def get_prompt(self) -> str:
        return "\n".join(f"{item['sender']}: {item['message']}" for item in self.history)