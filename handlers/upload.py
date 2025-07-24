from telegram import Update, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, filters

from utils.file_helpers import load_profiles, load_items, save_items
from handlers.start import show_main_menu

PHOTO, ITEM_NAME, CATEGORY, DESCRIPTION, WANTED_ITEM = range(5)

async def upload_item_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📸 Send a photo of the item you'd like to trade:")
    return PHOTO

async def receive_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    photo = update.message.photo[-1]
    file = await photo.get_file()
    photo_path = f"images/{user_id}_{photo.file_unique_id}.jpg"
    await file.download_to_drive(photo_path)

    context.user_data["photo"] = photo_path
    await update.message.reply_text("🔛 What is the name of the item?")
    return ITEM_NAME

async def receive_item_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text
    await update.message.reply_text("🍿 What category is it in? (e.g. football, gym, tennis, etc)")
    return CATEGORY

async def receive_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["category"] = update.message.text
    await update.message.reply_text("📜 Add a short description:")
    return DESCRIPTION

async def receive_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["description"] = update.message.text
    await update.message.reply_text("🎯 What item are you looking for in return?")
    return WANTED_ITEM

async def receive_wanted_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    profiles = load_profiles()

    if user_id not in profiles:
        await update.message.reply_text("❌ You must create a profile first.")
        return ConversationHandler.END

    profile = profiles[user_id]
    item = {
        "user_id": user_id,
        "photo": context.user_data["photo"],
        "name": context.user_data["name"],
        "category": context.user_data["category"],
        "description": context.user_data["description"],
        "wanted_item": update.message.text,
        "contact": profile["contact"]
    }

    items = load_items()
    items.append(item)
    save_items(items)

    await update.message.reply_text("✅ Your item has been uploaded!")
    await show_main_menu(update)
    return ConversationHandler.END

upload_conv = ConversationHandler(
    entry_points=[MessageHandler(filters.Regex("^(Upload New Item)$"), upload_item_start)],
    states={
        PHOTO: [MessageHandler(filters.PHOTO, receive_photo)],
        ITEM_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_item_name)],
        CATEGORY: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_category)],
        DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_description)],
        WANTED_ITEM: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_wanted_item)],
    },
    fallbacks=[]
)
