import os, sys, asyncio
from pathlib import Path
from dotenv import load_dotenv
import edge_tts
from edge_tts import exceptions as tts_exc

# Windows‑loop‑fix
import asyncio as _asyncio, sys as _sys
if _sys.platform.startswith("win"):
    from asyncio import WindowsSelectorEventLoopPolicy
    _asyncio.set_event_loop_policy(WindowsSelectorEventLoopPolicy())

load_dotenv()
VOICE    = os.getenv("EDGE_VOICE", "ru-RU-DmitryNeural")
TEMP_DIR = Path(os.getenv("TEMP_DIR", "./temp"))
TEMP_DIR.mkdir(exist_ok=True)

async def _synth(text: str, mp3_path: Path):
    com = edge_tts.Communicate(text=text, voice=VOICE)
    await com.save(str(mp3_path))

def synthesize(text: str, basename: str) -> Path:
    """
    Синтезирует текст → temp/basename.mp3
    """
    mp3_path = TEMP_DIR / f"{basename}.mp3"
    try:
        asyncio.run(_synth(text, mp3_path))
    except tts_exc.NoAudioReceived:
        print("Ошибка TTS: сервис не принял текст.", file=sys.stderr)
        raise SystemExit(1)
    return mp3_path
