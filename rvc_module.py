import os, sys
from pathlib import Path

# —— патчим torch.load для HuBERT словаря ——
import torch
import fairseq.data.dictionary
torch.serialization.add_safe_globals([fairseq.data.dictionary.Dictionary])

import soundfile as sf
import librosa
from dotenv import load_dotenv
from rvc.modules.vc.modules import VC

load_dotenv()
SCRIPT_DIR    = Path(__file__).parent
CHAR_DIR_ROOT = SCRIPT_DIR / "characters"

def revoice(character: str, mp3_path: Path, basename: str) -> Path:
    """
    Для персонажа character берёт temp/basename.mp3,
    конвертит → wav, прогоняет через его voice.pth и
    возвращает Path к temp/basename.wav
    """
    char_dir   = CHAR_DIR_ROOT / character
    model_pth  = char_dir / "voice.pth"
    index_root = char_dir

    # сохраняем старое, перезаписываем index_root
    prev = os.environ.get("index_root")
    os.environ["index_root"] = str(index_root)

    # 1) mp3 → wav
    wav_in = mp3_path.with_suffix(".wav")
    y, sr = librosa.load(str(mp3_path), sr=None)
    sf.write(str(wav_in), y, sr)

    # 2) загрузка и инференс
    vc = VC()
    vc.get_vc(str(model_pth))
    tgt_sr, audio_opt, *_ = vc.vc_single(1, wav_in)
    if audio_opt is None:
        print(f"RVC error: пустой результат для {character}", file=sys.stderr)
        sys.exit(1)

    # 3) сохранение и восстановление index_root
    out_wav = mp3_path.parent / f"{basename}.wav"
    sf.write(str(out_wav), audio_opt, tgt_sr)
    if prev is None:
        del os.environ["index_root"]
    else:
        os.environ["index_root"] = prev

    return out_wav
