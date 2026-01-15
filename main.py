
import logging
import asyncio 
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

# Modules
import link
import bio

# CONFIGURATION
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"  # Apna Token Dalein
OWNER_TAG = "@YourUsername"

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    # --- BUTTON LOGIC ---
    bot_username = context.bot.username
    add_group_url = f"https://t.me/{bot_username}?startgroup=true"
    
    keyboard = [
        [InlineKeyboardButton("➕ Add Me To Your Group ➕", url=add_group_url)],
        [InlineKeyboardButton("👑 Owner", url=f"https://t.me/{OWNER_TAG.replace('@', '')}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # --- UPDATED MESSAGE TEXT (Hinglish) ---
    welcome_text = (
        f"👋 <b>Namaste {user.first_name}!</b>\n\n"
        f"🛡 <b>Main hu Group Security Bot.</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"😤 <b>Mera Kaam:</b> <u>Main Group me koi Link nahi rahne dunga!</u>\n"
        f"🚀 <b>Super Fast:</b> Link aate hi turant delete karunga.\n"
        f"👤 <b>Anti-Bio:</b> User ke Bio me link hoga to wo bhi pakad lunga.\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"👑 <b>Maintainer:</b> {OWNER_TAG}\n"
        f"<i>Mujhe apne group me Add karein aur Admin banayein!</i> 👇"
    )
    
    await update.message.reply_text(
        text=welcome_text,
        parse_mode=ParseMode.HTML,
        reply_markup=reply_markup
    )

async def master_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # 1. Link Check (Local Text Check - Fast)
    if await link.check_message_link(update, context):
        return

    # 2. Bio Check (Cached - Fast)
    await bio.check_user_bio(update, context)

if __name__ == '__main__':
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("onbiolink", bio.set_bio_check))
    application.add_handler(CommandHandler("offbiolink", bio.set_bio_check))
    
    # Filters.ALL
    application.add_handler(MessageHandler(filters.ALL & (~filters.COMMAND), master_message_handler))

    print("Bot is running with Updated Start Message...")
    application.run_polling()
