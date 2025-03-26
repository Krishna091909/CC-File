import random
import humanize
from Script import script
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from info import URL, LOG_CHANNEL, SHORTLINK
from urllib.parse import quote_plus
from TechVJ.util.file_properties import get_name, get_hash, get_media_file_size
from TechVJ.util.human_readable import humanbytes
from database.users_chats_db import db
from utils import temp, get_shortlink

@Client.on_message(filters.command("start") & filters.incoming)
async def start(client, message):
    print("Received /start command from:", message.from_user.id)
    
    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id, message.from_user.first_name)
        await client.send_message(LOG_CHANNEL, script.LOG_TEXT_P.format(message.from_user.id, message.from_user.mention))

    rm = InlineKeyboardMarkup([[InlineKeyboardButton("✨ Update Channel", url="https://t.me/vj_botz")]])

    await client.send_message(
        chat_id=message.from_user.id,
        text=script.START_TXT.format(message.from_user.mention, temp.U_NAME, temp.B_NAME),
        reply_markup=rm,
        parse_mode=enums.ParseMode.HTML
    )

@Client.on_message(filters.private & (filters.document | filters.video))
async def stream_start(client, message):
    print("Received a file from:", message.from_user.id)
    
    try:
        file = getattr(message, message.media.value)
        if not file:
            print("❌ Error: File not found in message!")
            return

        filename = file.file_name
        filesize = humanize.naturalsize(file.file_size)
        fileid = file.file_id
        user_id = message.from_user.id
        username = message.from_user.mention

        print(f"✅ File Received: {filename} (Size: {filesize})")

        # Log the file in LOG_CHANNEL
        log_msg = await client.send_cached_media(chat_id=LOG_CHANNEL, file_id=fileid)
        print(f"✅ File logged in channel with Message ID: {log_msg.id}")

        fileName = quote_plus(get_name(log_msg))

        # Generate stream & download links
        if SHORTLINK == False:
            stream = f"{URL}watch/{log_msg.id}/{fileName}?hash={get_hash(log_msg)}"
            download = f"{URL}download/{log_msg.id}/{fileName}?hash={get_hash(log_msg)}"
        else:
            stream = await get_shortlink(f"{URL}watch/{log_msg.id}/{fileName}?hash={get_hash(log_msg)}")
            download = await get_shortlink(f"{URL}download/{log_msg.id}/{fileName}?hash={get_hash(log_msg)}")

        print(f"✅ Stream Link: {stream}")
        print(f"✅ Download Link: {download}")

        # Send message with links in LOG_CHANNEL
        await log_msg.reply_text(
            text=f"🔹 Links generated for {username}\n📂 {fileName}",
            quote=True,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🚀 Fast Download 🚀", url=download),
                 InlineKeyboardButton('🖥️ Watch online 🖥️', url=stream)]
            ])
        )

        # Send reply to the user
        rm = InlineKeyboardMarkup([
            [InlineKeyboardButton("🖥 Stream", url=stream),
             InlineKeyboardButton("📥 Download", url=download)]
        ])
        
        msg_text = """<i><u>🚀 Your Link is Ready!</u></i>\n\n<b>📂 File Name:</b> <i>{}</i>\n<b>📦 Size:</b> <i>{}</i>\n\n<b>📥 Download:</b> <i>{}</i>\n<b>🖥 Watch:</b> <i>{}</i>\n\n<b>🔹 Link is valid until deleted.</b>"""

        await message.reply_text(
            text=msg_text.format(filename, filesize, download, stream),
            quote=True,
            disable_web_page_preview=True,
            reply_markup=rm
        )
        
        print("✅ Message sent successfully to user!")

    except Exception as e:
        print(f"❌ Error: {e}")
