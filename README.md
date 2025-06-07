# AI_Kaiwa Discord Bot

Кратко: Discord-бот, который организует двусторонний диалог между персонажами Stasik и Valdos: их реплики сначала синтезируются через edge-tts, затем преобразуются в голоса моделей RVC, и воспроизводятся в голосовом канале.

## Функции

- Команда `!dialog <тема>` — запускает диалог на заданную тему.
- Команда `!stopdialog` — останавливает текущий диалог.
- Лог прогресса отображается в консоли с помощью прогресс-бара `tqdm`.

## Установка

```bash
#!/usr/bin/env bash
set -e

# 1. Установка Ollama и модели
curl -fsSL https://ollama.com/install.sh | sudo sh
ollama pull llama2-uncensored:7b

# 2. Установка ffmpeg (Ubuntu)
sudo apt update
sudo apt install -y ffmpeg

# 3. Установка Python-зависимостей
pip install --upgrade pip
pip install -r requirements.txt

# 4. Создание .env
cat > .env <<EOF
EDGE_VOICE=ru-RU-DmitryNeural
TEMP_DIR=./temp
OLLAMA_MODEL=llama2-uncensored:7b
HUBERT_PATH="C:/Program Files/RVC1006Nvidia/assets/hubert/hubert_base.pt"
rmvpe_root="C:/Program Files/RVC1006Nvidia/assets/rmvpe"
index_root=./characters/Stasik
DISCORD_TOKEN=ВАШ_DISCORD_TOKEN
VOICE_CHANNEL_ID=1132250821657100372
EOF

# 5. Создание папки temp
mkdir -p "${TEMP_DIR}"

# 6. Запуск бота
python bot.py
```

## Файлы проекта

- `bot.py` — реализация Discord-бота с командами `!dialog` и `!stopdialog`.
- `dialog_module.py` — интерфейс для генерации ответов через ollama.
- `tts.py` — синтез речи через edge-tts.
- `rvc_module.py` — переозвучка через RVC-модели.
- `characters/` — папки с моделями и системными промптами для каждого персонажа.
- `temp/` — папка для временных и выходных аудиофайлов.
- `requirements.txt` — список зависимостей проекта.

## Переменные окружения

Переменные в `.env`:

| Ключ               | Описание                                          |
|--------------------|---------------------------------------------------|
| `EDGE_VOICE`       | Голос edge-tts (например `ru-RU-DmitryNeural`)     |
| `TEMP_DIR`         | Папка для временных файлов (например `./temp`)     |
| `OLLAMA_MODEL`     | Модель ollama (например `llama2-uncensored:7b`)    |
| `HUBERT_PATH`      | Путь к `hubert_base.pt`                            |
| `rmvpe_root`       | Папка с `rmvpe.pt`                                 |
| `index_root`       | Путь к `.index` для RVC (перезаписывается на лету) |
| `DISCORD_TOKEN`    | Токен Discord-бота (секрет)                       |
| `VOICE_CHANNEL_ID` | ID голосового канала для воспроизведения           |

---