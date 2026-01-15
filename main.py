import logging
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

# --- IMPORT MODULES ---
# Hamne jo 2 files banayi hain, unhe yahan import kar rahe hain
import link
import bio

# --- CONFIGURATION ---
BOT_TOKEN = "8265358758:AAEh0w0gMyVadZWguiqrYQM6xegfpcy2wiA"  # Apna Token Yahan Dalein
OWNER_TAG = "@nsnns"

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# --- START COMMAND ---
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    welcome_text = (
        f"👋 <b>Hello {user.first_name}!</b>\n\n"
        f"🛡 <b>I am the Group Guardian Bot.</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"🚫 <b>Anti-Link:</b> Checks messages for links.\n"
        f"👤 <b>Anti-Bio:</b> Checks user Bio for links (Use /onbiolink).\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"👑 <b>Maintainer:</b> {OWNER_TAG}\n"
    )
    await update.message.reply_text(text=welcome_text, parse_mode=ParseMode.HTML)

# --- MASTER HANDLER (Sab kuch control karega) ---
async def master_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Ye function har message ko check karega.
    Step 1: Message ke andar Link hai? -> link.py check karega.
    Step 2: Agar message clean hai, to kya User ke Bio me Link hai? -> bio.py check karega.
    """
    
    # 1. Pehle check karo message me link hai ya nahi (link.py)
    is_deleted_by_link = await link.check_message_link(update, context)
    
    # Agar link.py ne message delete kar diya, to aage mat badho
    if is_deleted_by_link:
        return

    # 2. Agar message saaf hai, to ab BIO check karo (bio.py)
    # Ye tabhi chalega jab /onbiolink kiya gaya ho
    await bio.check_user_bio(update, context)


if __name__ == '__main__':
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # Commands
    application.add_handler(CommandHandler("start", start_command))
    
    # Bio Switch Commands (From bio.py)
    application.add_handler(CommandHandler("onbiolink", bio.set_bio_check))
    application.add_handler(CommandHandler("offbiolink", bio.set_bio_check))

    # All Messages Handler
    # Ye 'master_message_handler' ko call karega jo baaki files ko use karega
    application.add_handler(MessageHandler(filters.ALL & (~filters.COMMAND), master_message_handler))

    print("Bot is running with Separate Modules (Main + Link + Bio)...")
    application.run_polling()
