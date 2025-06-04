import os

API_KEY_PATH = "openai_api_key.txt"

def save_api_key(key: str):
    with open(API_KEY_PATH, "w", encoding="utf-8") as f:
        f.write(key.strip())

def load_api_key() -> str:
    try:
        with open(API_KEY_PATH, "r", encoding="utf-8") as f:
            return f.read().strip()
    except FileNotFoundError:
        return ""