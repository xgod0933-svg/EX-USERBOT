from telethon import TelegramClient, events
from telethon.tl.types import ChannelParticipantsAdmins
import asyncio

print("--- Telegram Allban Bot Setup ---")
api_id = int(input("Apni API ID daalo: "))
api_hash = input("Apna API Hash daalo: ")
BOT_TOKEN = input("Apna Bot Token daalo: ")

bot = TelegramClient('bot_session', api_id, api_hash).start(bot_token=BOT_TOKEN)

ALLOWED_USERNAME = "DETI_RAHO"

@bot.on(events.NewMessage(pattern=r"^/allban"))
async def allban_handler(event):
    if not event.is_group:
        await event.reply("Yeh command sirf groups mein kaam karega!")
        return

    sender = await event.get_sender()
    
    if not sender.username or sender.username.lower() != ALLOWED_USERNAME.lower():
        await event.reply("Bhai, aap is bot ko use nahi kar sakte! Yeh sirf authorised user ke liye hai.")
        return

    chat = await event.get_chat()
    
    admins = await bot.get_participants(chat, filter=ChannelParticipantsAdmins)
    admin_ids = [admin.id for admin in admins]

    status_msg = await event.reply("Ban process shuru ho raha hai (Target: 200 members in ~5 mins)...")
    count = 0
    target_limit = 200

    async for user in bot.iter_participants(chat):
        if count >= target_limit:
            break

        if user.id in admin_ids or user.bot:
            continue

        try:
            await bot.edit_permissions(chat, user.id, view_messages=False)
            count += 1
            await asyncio.sleep(1.5) 
        except Exception as e:
            print(f"Error banning {user.id}: {e}")

    await status_msg.edit(f"Task complete! 5 minute mein total {count} members ko ban kar diya gaya hai.")

print("Bot chal raha hai...")
bot.run_until_disconnected()
