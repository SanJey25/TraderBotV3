from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackQueryHandler, ContextTypes, ConversationHandler, MessageHandler, filters

from utils.file_helpers import load_items
from handlers.start import show_main_menu

SEARCH_TYPE, SEARCH_QUERY, SEARCH_DISPLAY = range(20, 23)

async def start_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔍 Common Search", callback_data="search_common")],
        [InlineKeyboardButton("📛 Search by Name", callback_data="search_name")],
        [InlineKeyboardButton("🎯 Search by Wanted Item", callback_data="search_wanted")]
    ])
    await update.message.reply_text("🔎 Choose a search type:", reply_markup=keyboard)
    return SEARCH_TYPE

async def handle_search_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["search_type"] = query.data
    await query.edit_message_text("💬 Send your search keyword:")
    return SEARCH_QUERY

async def perform_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyword = update.message.text.lower()
    search_type = context.user_data.get("search_type")

    items = load_items()
    matched = []
    for item in items:
        name = item.get("name", "").lower()
        category = item.get("category", "").lower()
        description = item.get("description", "").lower()
        wanted = item.get("wanted_item", "").lower()

        if ((search_type == "search_common" and (keyword in name or keyword in category or keyword in description or keyword in wanted)) or
            (search_type == "search_name" and keyword in name) or
            (search_type == "search_wanted" and keyword in wanted)):
            matched.append(item)

    if not matched:
        await update.message.reply_text("❌ No items found.")
        await show_main_menu(update)
        return ConversationHandler.END

    context.user_data["search_results"] = matched
    context.user_data["search_index"] = 0
    return await show_next_search_result(update, context)

async def show_next_search_result(update_or_query, context):
    results = context.user_data["search_results"]
    index = context.user_data.get("search_index", 0)

    if index >= len(results):
        await update_or_query.message.reply_text("🚫 No more items found.")
        await show_main_menu(update_or_query)
        return ConversationHandler.END

    item = results[index]
    caption = (
        f"📦 *{item['name']}*\n"
        f"🏷 Category: {item['category']}\n"
        f"📝 {item['description']}\n"
        f"🎯 Wants: {item['wanted_item']}\n"
        f"📞 Contact: [Hidden until matched ✅]"
    )

    buttons = InlineKeyboardMarkup([[ 
        InlineKeyboardButton("✅ Match", callback_data="search_match"),
        InlineKeyboardButton("❌ Pass", callback_data="search_pass")
    ]])

    with open(item['photo'], "rb") as img:
        await update_or_query.message.reply_photo(
            photo=img,
            caption=caption,
            parse_mode="Markdown",
            reply_markup=buttons
        )
    return SEARCH_DISPLAY

async def handle_search_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    action = query.data
    index = context.user_data.get("search_index", 0)
    results = context.user_data.get("search_results", [])

    if index >= len(results):
        await query.message.reply_text("🚫 No more items found.")
        await show_main_menu(query)
        return ConversationHandler.END

    item = results[index]

    if action == "search_pass":
        context.user_data["search_index"] += 1
        return await show_next_search_result(query, context)

    elif action == "search_match":
        contact = item.get("contact", "No contact provided.")
        await query.edit_message_reply_markup(reply_markup=None)
        await query.message.reply_text(f"✅ You matched with this item!\n\n📞 Contact: {contact}")
        await show_main_menu(query)
        return ConversationHandler.END

search_conv = ConversationHandler(
    entry_points=[MessageHandler(filters.Regex("^(Search Barter Items)$"), start_search)],
    states={
        SEARCH_TYPE: [CallbackQueryHandler(handle_search_type, pattern="^search_")],
        SEARCH_QUERY: [MessageHandler(filters.TEXT & ~filters.COMMAND, perform_search)],
        SEARCH_DISPLAY: [CallbackQueryHandler(handle_search_action, pattern="^search_(match|pass)$")],
    },
    fallbacks=[]
)
