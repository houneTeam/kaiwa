#!/usr/bin/env python3
"""
Discord-бот: диалог Stasik <-> Valdos с edge-tts и RVC.
Прогресс и красивые логи через tqdm.
"""
import os
import sys
import asyncio
import logging
import warnings
from pathlib import Path
from dotenv import load_dotenv

import discord
from discord.ext import commands
from tqdm import tqdm

from tts import synthesize
from rvc_module import revoice
from dialog_module import generate

# ========== Настройка логирования и фильтрация предупреждений ==========
logging.basicConfig(level=logging.WARNING)
logging.getLogger('discord').setLevel(logging.WARNING)
logging.getLogger('rvc').setLevel(logging.ERROR)
logging.getLogger('fairseq').setLevel(logging.ERROR)
logging.getLogger('httpx').setLevel(logging.ERROR)
logging.getLogger('faiss').setLevel(logging.ERROR)
warnings.filterwarnings('ignore', category=FutureWarning)

# ========== Загрузка окружения ==========
load_dotenv()
TOKEN            = os.getenv("DISCORD_TOKEN")
VOICE_CHANNEL_ID = int(os.getenv("VOICE_CHANNEL_ID", 0))
TEMP_DIR         = Path(os.getenv("TEMP_DIR", "./temp"))
TEMP_DIR.mkdir(exist_ok=True)
FFMPEG_PATH      = str(Path(__file__).parent / "ffmpeg.exe")

# ========== Инициализация бота ==========
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    tqdm.write(f"✅ Logged in as {bot.user} (ID: {bot.user.id})")

async def join_voice_channel():
    channel = bot.get_channel(VOICE_CHANNEL_ID)
    if not isinstance(channel, discord.VoiceChannel):
        raise RuntimeError(f"Voice channel {VOICE_CHANNEL_ID} not found.")
    vc = discord.utils.get(bot.voice_clients, guild=channel.guild)
    if vc:
        if vc.channel.id != VOICE_CHANNEL_ID:
            await vc.move_to(channel)
    else:
        vc = await channel.connect()
    return vc

async def play_audio(vc: discord.VoiceClient, path: Path):
    source = discord.FFmpegPCMAudio(str(path), executable=FFMPEG_PATH)
    vc.play(source)
    while vc.is_playing():
        await asyncio.sleep(0.2)

async def process_turn(vc: discord.VoiceClient, speaker: str, text: str, turn: int, pbar: tqdm):
    # Вывод в консоль поверх прогресса
    pbar.set_description(f"{speaker}[{turn:02d}]")
    tqdm.write(f"[{turn:02d}] {speaker}: {text}")
    # 1) edge-tts → mp3
    mp3 = await asyncio.to_thread(synthesize, text, f"{speaker}_{turn}")
    # 2) RVC → wav
    wav = await asyncio.to_thread(revoice, speaker, mp3, f"{speaker}_{turn}")
    # 3) воспроизведение
    await play_audio(vc, wav)
    pbar.update(1)

async def run_dialog(ctx, topic: str):
    vc = await join_voice_channel()
    # шагов: анонс + первый + 5*2 обменов
    total = 1 + 1 + 5*2
    pbar = tqdm(total=total, dynamic_ncols=True, bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} turns")
    try:
        # анонс темы
        announcement = f"Диалог на тему «{topic}»"
        tqdm.write(f"🔊 Announcement: {announcement}")
        ann_mp3 = await asyncio.to_thread(synthesize, announcement, "topic_announcement")
        await play_audio(vc, Path(ann_mp3))
        pbar.update(1)

        history = {"Stasik": [], "Valdos": []}
        # первый ход Stasik
        init_msg = f"Привет, Valdos! Давай поговорим на тему: {topic}"
        history["Stasik"].append({"role":"user","content":init_msg})
        reply = await asyncio.to_thread(generate, "Stasik", history["Stasik"])
        history["Valdos"].append({"role":"user","content":reply})
        await process_turn(vc, "Stasik", reply, 0, pbar)

        # последующие ходы
        for i in range(1, 6):
            for speaker, listener in [("Valdos","Stasik"), ("Stasik","Valdos")]:
                reply = await asyncio.to_thread(generate, speaker, history[speaker])
                history[listener].append({"role":"user","content":reply})
                await process_turn(vc, speaker, reply, i, pbar)
    except asyncio.CancelledError:
        tqdm.write("⏹️ Dialog was stopped.")
    finally:
        pbar.close()
        await vc.disconnect()
        await ctx.reply("✅ Диалог завершён.")

@bot.command(name="dialog")
async def dialog(ctx, *, topic: str):
    if hasattr(bot, "dialog_task") and not bot.dialog_task.done():
        return await ctx.reply("⚠️ Диалог уже запущен.")
    bot.dialog_task = bot.loop.create_task(run_dialog(ctx, topic))
    await ctx.reply(f"▶️ Запущен диалог на тему: {topic}")

@bot.command(name="stopdialog")
async def stopdialog(ctx):
    task = getattr(bot, "dialog_task", None)
    if task and not task.done():
        task.cancel()
        await ctx.reply("⏹ Диалог остановлен.")
    else:
        await ctx.reply("❌ Нет активного диалога.")

if __name__ == "__main__":
    bot.run(TOKEN)
