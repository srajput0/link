import re
import asyncio
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

# Bio Checking ka Status (On/Off) memory me save karne ke liye
# Note: Bot restart hone par ye reset ho jayega (Database use karein permanent ke liye)
BIO_SETTINGS = {}

# --- COMMANDS: ON / OFF ---
async def set_bio_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user = update.effective_user
    args = context.args
    
    # Check Admin Rights (Optional implementation, abhi direct command hai)
    admins = await context.bot.get_chat_administrators(chat_id)
    if user.id not in [admin.user.id for admin in admins]:
        await update.message.reply_text("🚫 सिर्फ एडमिन इस सेटिंग को बदल सकते हैं!")
        return

    # Command logic
    query = update.message.text.lower()
    
    if "/onbiolink" in query:
        BIO_SETTINGS[chat_id] = True
        await update.message.reply_text("✅ <b>Bio Link Check Enabled!</b>\nअब जिसके Bio में लिंक होगा, उसका मैसेज डिलीट होगा।", parse_mode=ParseMode.HTML)
    elif "/offbiolink" in query:
        BIO_SETTINGS[chat_id] = False
        await update.message.reply_text("❌ <b>Bio Link Check Disabled!</b>\nअब Bio चेक नहीं किया जाएगा।", parse_mode=ParseMode.HTML)

# --- CORE LOGIC: CHECK USER BIO ---
async def check_user_bio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Returns True if message deleted due to Bio Link, else False"""
    chat_id = update.effective_chat.id
    user = update.effective_user
    message = update.effective_message

    # 1. Check if Feature is ON
    if not BIO_SETTINGS.get(chat_id, False):
        return False  # Off hai to return karo

    # 2. Skip Bots & Admins (Optional: Agar admin ka bio check nahi karna)
    if user.is_bot:
        return False
        
    try:
        admins = await context.bot.get_chat_administrators(chat_id)
        if user.id in [admin.user.id for admin in admins]:
            return False # Admin allowed
    except:
        pass

    # 3. Get User Full Info (Bio fetch karne ke liye)
    try:
        # Telegram API se user ki details nikalo
        user_full_info = await context.bot.get_chat(user.id)
        user_bio = user_full_info.bio or ""
        
        # 4. Check Link in Bio
        url_pattern = r'(https?://|www\.|t\.me/|@)'
        if re.search(url_pattern, user_bio):
            # LINK FOUND IN BIO! DELETE MESSAGE
            try:
                await message.delete()
                
                warning_msg = (
                    f"⚠️ <b>BIO LINK DETECTED</b>\n"
                    f"━━━━━━━━━━━━━━━━━━\n"
                    f"👤 <b>User:</b> <a href='tg://user?id={user.id}'>{user.first_name}</a>\n"
                    f"🚫 आपके Telegram Bio में लिंक या यूजरनेम है।\n"
                    f"group में मैसेज करने के लिए उसे हटा दें!\n"
                    f"━━━━━━━━━━━━━━━━━━\n"
                    f"<i>🗑 Message deleted. Warning auto-deletes in 5s.</i>"
                )
                
                sent_msg = await context.bot.send_message(
                    chat_id=chat_id,
                    text=warning_msg,
                    parse_mode=ParseMode.HTML
                )
                
                # Wait and Delete Warning
                await asyncio.sleep(5)
                await sent_msg.delete()
                return True # Message delete ho gaya

            except Exception as e:
                print(f"Error deleting bio-spam: {e}")
                
    except Exception as e:
        # Privacy settings ki wajah se kabhi kabhi bio nahi milta
        print(f"Bio check error: {e}")

    return False
