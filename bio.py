
import re
import asyncio
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

# --- SETTINGS ---
BIO_SETTINGS = {} 
# Cache: User ID save karega taaki bar-bar Telegram se na puchna pade (Speed Boost)
USER_BIO_CACHE = {} 

# --- COMMANDS ---
async def set_bio_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    query = update.message.text.lower()
    
    if "/onbiolink" in query:
        BIO_SETTINGS[chat_id] = True
        await update.message.reply_text("✅ <b>Fast Bio-Check Enabled!</b>", parse_mode=ParseMode.HTML)
    elif "/offbiolink" in query:
        BIO_SETTINGS[chat_id] = False
        USER_BIO_CACHE.clear() # Cache clear kar do
        await update.message.reply_text("❌ <b>Bio-Check Disabled!</b>", parse_mode=ParseMode.HTML)

# --- BACKGROUND TASK (Warning Delete Karne Ke Liye) ---
async def send_warning_and_delete(context, chat_id, user_id, first_name):
    """Ye function background me chalega taaki bot ruke nahi"""
    try:
        warning_msg = (
            f"⚠️ <b>BIO LINK DETECTED</b>\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"👤 <b>User:</b> <a href='tg://user?id={user_id}'>{first_name}</a>\n"
            f"🚫 <b>Action:</b> Message Deleted.\n"
            f"💡 <i>Reason: Link found in your Bio.</i>\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"<i>⏳ Auto-cleaning...</i>"
        )
        
        # Warning Bhejo
        sent_msg = await context.bot.send_message(
            chat_id=chat_id,
            text=warning_msg,
            parse_mode=ParseMode.HTML
        )
        
        # 5 Second Ruko (Background me)
        await asyncio.sleep(5)
        
        # Warning Delete Karo
        await sent_msg.delete()
    except Exception as e:
        print(f"Background warning error: {e}")

# --- MAIN CHECK LOGIC ---
async def check_user_bio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Returns True if spam found, else False.
    Ab ye function rukega nahi, turant return karega.
    """
    chat_id = update.effective_chat.id
    user = update.effective_user
    message = update.effective_message

    # 1. Check if Feature is ON
    if not BIO_SETTINGS.get(chat_id, False):
        return False

    # 2. Skip Bots & Admins (Admin check bhi cache kar sakte hain speed ke liye)
    if user.is_bot:
        return False
    
    # --- CACHE CHECK (SPEED BOOST) ---
    # Agar hume pehle se pata hai ki is user ka bio Ganda hai, to seedha delete karo
    # Bar bar Telegram API call karne se bot slow hota hai.
    
    is_bad_bio = False
    
    # Kya ye user Cache me hai?
    if user.id in USER_BIO_CACHE:
        is_bad_bio = USER_BIO_CACHE[user.id]
    else:
        # Cache me nahi hai, to Telegram se pucho (Sirf pehli baar)
        try:
            admins = await context.bot.get_chat_administrators(chat_id)
            if user.id in [admin.user.id for admin in admins]:
                return False # Admin hai

            user_full_info = await context.bot.get_chat(user.id)
            user_bio = user_full_info.bio or ""
            
            # Check Link
            url_pattern = r'(https?://|www\.|t\.me/|@)'
            if re.search(url_pattern, user_bio):
                is_bad_bio = True
            else:
                is_bad_bio = False
            
            # Result ko Cache me daal do
            USER_BIO_CACHE[user.id] = is_bad_bio
            
        except Exception as e:
            print(f"Bio fetch error: {e}")
            return False

    # --- ACTION ---
    if is_bad_bio:
        try:
            # 1. Message Delete (Turant)
            await message.delete()
            
            # 2. Warning Task (Background me daal do)
            # asyncio.create_task ka matlab: "Tum apna kaam karo, main agla message dekhta hu"
            asyncio.create_task(send_warning_and_delete(context, chat_id, user.id, user.first_name))
            
            return True
        except Exception as e:
            print(f"Delete error: {e}")

    return False
