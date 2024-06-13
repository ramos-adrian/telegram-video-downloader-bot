import asyncio
import json
import logging
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, filters, Application
import os
from src.utils import is_video_url, get_video_info, get_file_size, get_duration, download

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

BOT_TOKEN = os.environ['BOT_TOKEN']
MAX_DURATION = float(os.environ['MAX_DURATION'])
MAX_FILE_SIZE = float(os.environ['MAX_FILE_SIZE'])
CHAT_ID = int(os.environ['CHAT_ID'])

application = Application.builder().token(BOT_TOKEN).build()


def get_video_url(message):
    if len(message.entities) == 0:
        return None
    first_entity = message.entities[0]
    url = message.text[first_entity.offset: first_entity.offset + first_entity.length]
    if not is_video_url(url):
        return None
    return url


async def vermeme(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = get_video_url(update.message.reply_to_message)
    if url is None:
        await update.message.reply_text('No contiene la URL de un video', quote=True)
        return

    try:
        sanitized_video_info = get_video_info(url)
    except Exception as e:
        await update.message.reply_text('El video no se pudo descargar', quote=True)
        return

    try:
        file_size = get_file_size(sanitized_video_info)
    except Exception as e:
        pass
    else:
        if file_size > MAX_FILE_SIZE:
            await update.message.reply_text('El tamaño del archivo es demasiado grande', quote=True)
            return

    try:
        duration = get_duration(sanitized_video_info)
    except Exception as e:
        await update.message.reply_text('El video no se pudo descargar', quote=True)
        return
    else:
        if duration > MAX_DURATION:
            await update.message.reply_text('El video es demasiado largo', quote=True)
            return

    await update.message.reply_text('Descargando video...', quote=True)
    file_name = download(url)
    await update.message.reply_video(video=open(f'/tmp/{file_name}.mp4', 'rb'), quote=True, disable_notification=True)


async def main(event, context):
    ver_meme_handler = CommandHandler('vermeme', vermeme,
                                      filters=
                                      filters.REPLY &
                                      filters.ChatType.GROUPS &
                                      filters.Chat(chat_id=CHAT_ID)
                                      )
    application.add_handler(ver_meme_handler)

    try:
        await application.initialize()
        await application.process_update(
            Update.de_json(json.loads(event["body"]), application.bot)
        )

        return {
            'statusCode': 200,
            'body': 'Success'
        }

    except Exception as exc:
        return {
            'statusCode': 500,
            'body': 'Failure'
        }


def handler(event, context):
    return asyncio.get_event_loop().run_until_complete(main(event, context))
