from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import CommandHandler, ContextTypes



async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    from utils.file_helpers import load_profiles

    profiles = load_profiles()
    if user_id not in profiles:
        await update.message.reply_text(
            "👋 Welcome to Barter Bot!\nYou need to create a profile to continue.",
            reply_markup=ReplyKeyboardMarkup([["Create Profile"]], resize_keyboard=True)
        )
    else:
        await show_main_menu(update)

async def show_main_menu(update_or_query):
    buttons = [
        ["My Profile", "My Items"],
        ["Search Barter Items", "Upload New Item"]
    ]
    if hasattr(update_or_query, "message"):
        await update_or_query.message.reply_text("📋 Main Menu:", reply_markup=ReplyKeyboardMarkup(buttons, resize_keyboard=True))
    elif hasattr(update_or_query, "callback_query"):
        await update_or_query.callback_query.message.reply_text("📋 Main Menu:", reply_markup=ReplyKeyboardMarkup(buttons, resize_keyboard=True))

start_handler = CommandHandler("start", start)
