import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackQueryHandler, ContextTypes, ConversationHandler, MessageHandler, filters

from utils.file_helpers import load_items, save_items
from handlers.start import show_main_menu

EDIT_FIELD_SELECTION, EDIT_NEW_VALUE = range(10, 12)

async def show_my_items(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    items = load_items()
    user_items = [item for item in items if item.get("user_id") == user_id]

    if not user_items:
        await update.message.reply_text("📭 You haven't uploaded any items yet.")
        return

    context.user_data["my_items"] = user_items

    for index, item in enumerate(user_items):
        caption = (
            f"📦 *{item['name']}*\n"
            f"🏷 Category: {item['category']}\n"
            f"📝 {item['description']}\n"
            f"🎯 Wants: {item['wanted_item']}"
        )
        buttons = InlineKeyboardMarkup([[  
            InlineKeyboardButton("✏️ Edit", callback_data=f"edit_{index}"),
            InlineKeyboardButton("🗑 Delete", callback_data=f"delete_{index}")
        ]])
        with open(item["photo"], "rb") as img:
            await update.message.reply_photo(photo=img, caption=caption, parse_mode="Markdown", reply_markup=buttons)

async def handle_item_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    index = int(data.split("_")[1])
    context.user_data["edit_index"] = index

    if data.startswith("edit_"):
        buttons = InlineKeyboardMarkup([[  
            InlineKeyboardButton("📦 Name", callback_data="field_name"),
            InlineKeyboardButton("🏷 Category", callback_data="field_category")
        ], [
            InlineKeyboardButton("📝 Description", callback_data="field_description"),
            InlineKeyboardButton("🎯 Wanted Item", callback_data="field_wanted")
        ]])
        await query.message.reply_text("✏️ What would you like to edit?", reply_markup=buttons)
        return EDIT_FIELD_SELECTION

    elif data.startswith("delete_"):
        items = load_items()
        user_items = [item for item in items if item.get("user_id") == str(query.from_user.id)]

        global_index = None
        found_count = -1
        for i, it in enumerate(items):
            if it.get("user_id") == str(query.from_user.id):
                found_count += 1
                if found_count == index:
                    global_index = i
                    break
        if global_index is not None:
            photo_path = items[global_index]["photo"]
            if os.path.exists(photo_path):
                os.remove(photo_path)
            del items[global_index]
            save_items(items)

        await query.message.reply_text("🗑 Item deleted successfully.")
        await show_main_menu(query)
        return ConversationHandler.END

async def choose_edit_field(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    field_map = {
        "field_name": "name",
        "field_category": "category",
        "field_description": "description",
        "field_wanted": "wanted_item"
    }
    context.user_data["edit_field"] = field_map[query.data]
    await query.message.reply_text("✍️ Send the new value:")
    return EDIT_NEW_VALUE

async def update_item_field(update: Update, context: ContextTypes.DEFAULT_TYPE):
    new_value = update.message.text
    field = context.user_data["edit_field"]
    edit_index = context.user_data["edit_index"]

    items = load_items()
    global_index = None
    found_count = -1
    for i, it in enumerate(items):
        if it.get("user_id") == str(update.message.from_user.id):
            found_count += 1
            if found_count == edit_index:
                global_index = i
                break
    if global_index is not None:
        items[global_index][field] = new_value
        save_items(items)

    await update.message.reply_text("✅ Item updated successfully.")
    await show_main_menu(update)
    return ConversationHandler.END

edit_conv = ConversationHandler(
    entry_points=[CallbackQueryHandler(handle_item_action, pattern="^(edit_|delete_)\d+$")],
    states={
        EDIT_FIELD_SELECTION: [CallbackQueryHandler(choose_edit_field, pattern="^field_")],
        EDIT_NEW_VALUE: [MessageHandler(filters.TEXT & ~filters.COMMAND, update_item_field)],
    },
    fallbacks=[]
)

show_my_items_handler = MessageHandler(filters.Regex("^(My Items)$"), show_my_items)
