import re
import asyncio
from telegram import Update, MessageEntity
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

# --- BACKGROUND TASK (Warning + Auto Delete) ---
async def send_link_warning(context, chat_id, user_id, first_name, reason_text):
    """
    Ye function background me chalega (Async Task).
    Iske chalne se Bot rukega nahi.
    """
    try:
        warning_msg = (
            f"⚠️ <b>RESTRICTED ACTION</b>\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"👤 <b>User:</b> <a href='tg://user?id={user_id}'>{first_name}</a>\n"
            f"{reason_text}\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"<i>🗑 Auto-deleting in 3 seconds...</i>"
        )

        sent_warning = await context.bot.send_message(
            chat_id=chat_id,
            text=warning_msg,
            parse_mode=ParseMode.HTML,
            protect_content=True
        )
        
        # 3 Second wait (Background me)
        await asyncio.sleep(3)
        
        # Delete Warning
        await sent_warning.delete()
    except Exception as e:
        print(f"Link warning error: {e}")

# --- MAIN LOGIC ---
async def check_message_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Returns True if message deleted, False if allowed.
    Non-blocking version.
    """
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat

    # Safety Check
    if not user or user.id == context.bot.id:
        return False

    # --- 1. DETECT SPAM (Link/Username) ---
    found_spam = False
    
    # Entities Check (Hidden Links)
    entities = message.entities or message.caption_entities
    if entities:
        for entity in entities:
            if entity.type in [MessageEntity.URL, MessageEntity.TEXT_LINK, MessageEntity.EMAIL, MessageEntity.MENTION]:
                found_spam = True
                break

    # Regex Check (Raw Text)
    if not found_spam:
        text_to_check = message.text or message.caption or ""
        spam_pattern = r'(https?://|www\.|t\.me/|@)'
        if re.search(spam_pattern, text_to_check):
            found_spam = True

    if not found_spam:
        return False # Sab clean hai

    # --- 2. DECISION LOGIC (Admin Check) ---
    should_delete = False
    reason_text = ""

    if user.is_bot:
        should_delete = True
        reason_text = "🤖 <b>Bot Detected:</b> Bots are not allowed here!"
    else:
        # Check Admin Status
        try:
            admins = await context.bot.get_chat_administrators(chat.id)
            admin_ids = [admin.user.id for admin in admins]
            if user.id not in admin_ids:
                should_delete = True
                reason_text = "🚫 <b>No Links:</b> Only Admins can send links."
        except:
            # Agar admin check fail ho jaye, to safe side ke liye kuch mat karo
            return False

    # --- 3. FAST ACTION (Non-Blocking) ---
    if should_delete:
        try:
            # A. TURANT DELETE (Priority 1)
            await message.delete()
            
            # B. WARNING TASK (Priority 2 - Background)
            # asyncio.create_task() ka matlab hai:
            # "Tum warning ka kaam sambhalo, main agla message check karne ja raha hu"
            asyncio.create_task(
                send_link_warning(context, chat.id, user.id, user.first_name, reason_text)
            )
            
            return True # Delete ho gaya, turant return karo
        except Exception as e:
            print(f"Error in fast delete: {e}")

    return False
    
