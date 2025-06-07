#!/usr/bin/env python3
import os, time, sys
from pathlib import Path
from dotenv import load_dotenv
from dialog_module import generate
from tts import synthesize
from rvc_module import revoice

# Загружаем настройки
load_dotenv()
TEMP_DIR = Path(os.getenv("TEMP_DIR", "./temp"))
TEMP_DIR.mkdir(exist_ok=True)

# Функция воспроизведения любого аудиофайла
def play(path: Path):
    if sys.platform.startswith("win"):
        os.system(f'start "" "{path}"')
    else:
        print(f"[Audio saved] {path}")

# Обработка одного хода: синтез → переозвучка → воспроизведение
def process_turn(speaker: str, text: str, turn: int):
    print(f"\n[{turn:02d}] {speaker} говорит:")
    print(f"    “{text}”")

    # 1) edge-tts → mp3
    mp3 = synthesize(text, f"{speaker}_{turn}")
    print(f"    ▶ TTS mp3: {mp3.name}")

    # 2) RVC → wav
    wav = revoice(speaker, mp3, f"{speaker}_{turn}")
    print(f"    ▶ RVC wav: {wav.name}")

    # 3) воспроизведение
    play(wav)

# Точка входа
def main():
    characters = ["Stasik", "Valdos"]
    history = {c: [] for c in characters}

    topic = input("Введите тему диалога: ").strip()
    if not topic:
        print("Отменено.", file=sys.stderr)
        return

    # Дикторское объявление темы обычным TTS
    announcement = f"Диалог на тему «{topic}»"
    print(f"\n=== {announcement} ===")
    ann_mp3 = synthesize(announcement, "topic_announcement")
    play(ann_mp3)

    # Первый ход Stasik
    init_msg = f"Привет, Valdos! Давай поговорим на тему: {topic}"
    history["Stasik"].append({"role": "user", "content": init_msg})
    reply = generate("Stasik", history["Stasik"])
    history["Valdos"].append({"role": "user", "content": reply})
    process_turn("Stasik", reply, 0)

    # Чередуем реплики
    for i in range(1, 6):
        for speaker, listener in [("Valdos", "Stasik"), ("Stasik", "Valdos")]:
            reply = generate(speaker, history[speaker])
            history[listener].append({"role": "user", "content": reply})
            process_turn(speaker, reply, i)
            time.sleep(1)

if __name__ == "__main__":
    main()
