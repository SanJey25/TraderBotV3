import os
from dotenv import load_dotenv  # <-- import this
from telegram.ext import ApplicationBuilder
from handlers import start, profile, upload, my_items, search

def main():
    os.makedirs("images", exist_ok=True)
    os.makedirs("data", exist_ok=True)

    load_dotenv()  # <-- load variables from .env file

    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError("ERROR: TELEGRAM_BOT_TOKEN not found in environment variables")

    app = ApplicationBuilder().token(token).build()

    # Add handlers from different modules
    app.add_handler(start.start_handler)
    app.add_handler(profile.profile_conv)
    app.add_handler(upload.upload_conv)
    app.add_handler(my_items.edit_conv)
    app.add_handler(search.search_conv)

    app.add_handler(profile.show_profile_handler)
    app.add_handler(my_items.show_my_items_handler)

    print("🤖 Bot running...", flush=True)
    app.run_polling()

if __name__ == "__main__":
    main()
