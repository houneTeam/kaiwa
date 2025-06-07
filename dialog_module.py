import os
import ollama
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
MODEL = os.getenv("OLLAMA_MODEL", "llama2-uncensored:7b")

PROMPTS = {
    "Stasik": Path("characters/Stasik/prompt.txt"),
    "Valdos": Path("characters/Valdos/prompt.txt"),
}

def load_prompt(character: str) -> str:
    return PROMPTS[character].read_text(encoding="utf-8")

def generate(character: str, history: list) -> str:
    """
    История — list of {"role":..., "content":...}.
    Возвращает строчку ответа.
    """
    system = load_prompt(character)
    msgs   = [{"role":"system", "content":system}] + history
    resp   = ollama.chat(model=MODEL, messages=msgs)
    return resp["message"]["content"]
