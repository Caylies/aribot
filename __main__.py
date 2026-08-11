import os

import django
from dotenv import load_dotenv

from app.core.bot import Bot

load_dotenv()

TOKEN = os.getenv("TOKEN")

def main():
    if not TOKEN:
        raise ValueError("'TOKEN' is not set in the environment variables.")

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "models.models.settings")
    django.setup()

    bot = Bot()
    bot.run(TOKEN)

if __name__ == "__main__":
    main()
