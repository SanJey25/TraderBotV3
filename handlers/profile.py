from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, filters

from utils.file_helpers import load_profiles, save_profiles
from handlers.start import show_main_menu

PROFILE_NAME, PROFILE_CONTACT = range(2)

async def create_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👤 What is your name?", reply_markup=ReplyKeyboardRemove())
    return PROFILE_NAME

async def get_profile_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text
    await update.message.reply_text("📞 Now enter your contact (phone, Telegram username, etc):")
    return PROFILE_CONTACT

async def get_profile_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    name = context.user_data["name"]
    contact = update.message.text

    profiles = load_profiles()
    profiles[user_id] = {"name": name, "contact": contact}
    save_profiles(profiles)

    await update.message.reply_text("✅ Profile created successfully!")
    await show_main_menu(update)
    return ConversationHandler.END

async def show_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    profiles = load_profiles()
    if user_id not in profiles:
        await update.message.reply_text("❌ No profile found.")
        return
    profile = profiles[user_id]
    await update.message.reply_text(
        f"👤 *Your Profile:*\n\n"
        f"🧑 Name: {profile['name']}\n"
        f"📞 Contact: {profile['contact']}",
        parse_mode="Markdown"
    )

profile_conv = ConversationHandler(
    entry_points=[MessageHandler(filters.Regex("^(Create Profile)$"), create_profile)],
    states={
        PROFILE_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_profile_name)],
        PROFILE_CONTACT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_profile_contact)],
    },
    fallbacks=[]
)

show_profile_handler = MessageHandler(filters.Regex("^(My Profile)$"), show_profile)
