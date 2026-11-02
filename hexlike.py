import asyncio
from telethon import TelegramClient, events, errors

print("--- Telegram Interactive Userbot Setup ---")

try:
    API_ID = int(input("Apna Telegram API ID daalein (e.g. 1234567): "))
except ValueError:
    print("❌ Galat API ID! Sirf numbers hone chahiye.")
    exit()

API_HASH = input("Apna Telegram API Hash daalein: ").strip()

if not API_HASH:
    print("❌ API Hash khali nahi ho sakta!")
    exit()

# Client initialize
client = TelegramClient('tele_session', API_ID, API_HASH)

# Default custom messages list
custom_spam_messages = [
    "Suno",
    "Kahan gayab ho?",
    "Reply karo"
]

# State variables
is_spamming = False
adding_messages = False
default_delay = 3.0  # Default safe gap

# Helper function: Notification ko Saved Messages me bhejo aur 10 sec baad delete karo
async def send_log(text):
    try:
        msg = await client.send_message('me', text)
        asyncio.create_task(delete_after_delay(msg, 10))
    except Exception:
        pass

@client.on(events.NewMessage(outgoing=True))
async def command_handler(event):
    global is_spamming, adding_messages, custom_spam_messages, default_delay
    text = event.raw_text.strip()
    parts = text.split(" ", 1)
    cmd = parts[0].lower()

    # Apni command wala message chat se turant delete kar do taaki clean rahe
    if cmd in ["xo", "ox", "off"] or text.lower().startswith("done"):
        try:
            await event.delete()
        except Exception:
            pass

    # 1. XO COMMAND (Messages Add Karna Shuru)
    if cmd == "xo":
        adding_messages = True
        custom_spam_messages = []
        await send_log("Messages add karne ka mode on ho gaya hai. Aap jitne marzi messages bhejein. Jab ho jaye tab **done** ya **done [delay]** likhein.")
        return

    # Agar adding_messages mode on hai
    if adding_messages:
        text_lower = text.lower()
        if text_lower.startswith("done"):
            adding_messages = False
            
            done_parts = text.split(" ")
            if len(done_parts) > 1:
                try:
                    default_delay = float(done_parts[1])
                except ValueError:
                    pass
            
            await send_log(f"Sare messages save ho gaye! Total: {len(custom_spam_messages)} | Delay set: {default_delay}s")
        else:
            custom_spam_messages.append(text)
        return

    # 2. OX COMMAND (Spam Start - Unlimited until 'off')
    if cmd == "ox":
        if is_spamming:
            await send_log("Spamming pehle se hi chal rahi hai.")
            return
        
        if not event.is_reply:
            await send_log("Pehle kisi message par reply karein.")
            return
        
        delay = default_delay
        if len(parts) > 1:
            try:
                delay = float(parts[1].split()[0])
            except ValueError:
                pass

        await start_spamming(event, delay=delay, custom_msgs=custom_spam_messages)

    # 3. OFF COMMAND (Spam Stop)
    elif cmd == "off":
        if is_spamming:
            is_spamming = False
            await send_log("Spamming rok di gayi hai.")
        else:
            await send_log("Koi spamming nahi chal rahi hai.")


async def start_spamming(event, delay, custom_msgs):
    global is_spamming
    is_spamming = True
    chat = await event.get_chat()
    
    if not custom_msgs:
        await send_log("Koi messages available nahi hain! Pehle 'xo' likh kar messages add karein.")
        is_spamming = False
        return

    try:
        reply_msg = await event.get_reply_message()
        target_user = await reply_msg.get_sender()
        
        first_name = target_user.first_name if target_user.first_name else ""
        last_name = target_user.last_name if target_user.last_name else ""
        
        if first_name or last_name:
            user_profile_name = f"{first_name} {last_name}".strip()
        elif target_user.username:
            user_profile_name = f"@{target_user.username}"
        else:
            user_profile_name = "User"
            
        target_msg_id = reply_msg.id
        target_user_id = target_user.id
    except Exception as e:
        await send_log(f"Error: {e}")
        is_spamming = False
        return

    await send_log(f"Spamming shuru ho gayi hai (Delay: {delay}s, Unlimited round-by-round)...")

    idx = 0
    while is_spamming:  # Unlimited loop jab tak 'off' na likho
        msg_text = custom_msgs[idx % len(custom_msgs)]
        full_msg = f"[{user_profile_name}](tg://user?id={target_user_id}) {msg_text}"
        
        try:
            # Typing effect
            async with client.action(chat, 'typing'):
                await asyncio.sleep(0.4)
                sent_msg = await client.send_message(chat, full_msg, reply_to=target_msg_id, parse_mode='md')
                
            asyncio.create_task(delete_after_delay(sent_msg, 1))
            
        except errors.FloodWaitError as e:
            await send_log(f"FloodWait: {e.seconds} seconds ka wait...")
            await asyncio.sleep(e.seconds)
        except Exception:
            pass
        
        idx += 1
        await asyncio.sleep(delay)

    is_spamming = False
    await send_log("Spamming rok di gayi.")

async def delete_after_delay(message, delay_seconds):
    await asyncio.sleep(delay_seconds)
    try:
        await message.delete()
    except Exception:
        pass

print("Userbot start ho gaya hai...")
client.start()
client.run_until_disconnected()
