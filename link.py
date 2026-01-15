import re
import asyncio
from telegram import Update, MessageEntity
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

async def check_message_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Returns True if message deleted due to Link inside message, else False"""
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat

    if not user or user.id == context.bot.id:
        return False

    # --- CHECK FOR SPAM ---
    found_spam = False
    
    entities = message.entities or message.caption_entities
    if entities:
        for entity in entities:
            if entity.type in [MessageEntity.URL, MessageEntity.TEXT_LINK, MessageEntity.EMAIL, MessageEntity.MENTION]:
                found_spam = True
                break

    if not found_spam:
        text_to_check = message.text or message.caption or ""
        spam_pattern = r'(https?://|www\.|t\.me/|@)'
        if re.search(spam_pattern, text_to_check):
            found_spam = True

    if not found_spam:
        return False

    # --- DECISION LOGIC ---
    should_delete = False
    reason_text = ""

    if user.is_bot:
        should_delete = True
        reason_text = "🤖 <b>Bot Detected:</b> Bots are not allowed here!"
    else:
        try:
            admins = await context.bot.get_chat_administrators(chat.id)
            admin_ids = [admin.user.id for admin in admins]
            if user.id not in admin_ids:
                should_delete = True
                reason_text = "🚫 <b>No Links:</b> Only Admins can send links."
        except:
            return False

    # --- EXECUTION ---
    if should_delete:
        try:
            await message.delete()
            
            warning_msg = (
                f"⚠️ <b>RESTRICTED ACTION</b>\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"👤 <b>User:</b> <a href='tg://user?id={user.id}'>{user.first_name}</a>\n"
                f"{reason_text}\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"<i>🗑 Auto-deleting in 3 seconds...</i>"
            )

            sent_warning = await context.bot.send_message(
                chat_id=chat.id,
                text=warning_msg,
                parse_mode=ParseMode.HTML,
                protect_content=True
            )
            
            await asyncio.sleep(3)
            await sent_warning.delete()
            return True # Delete ho gaya

        except Exception as e:
            print(f"Error: {e}")

    return False
