from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from config import DB_NAME
from utils.database import Database


db = Database(DB_NAME)


# Function for make inline keyboards from category names
def make_category_list() -> InlineKeyboardMarkup:
    categories = db.get_categories()
    rows = []
    for category in categories:
        rows.append([
            InlineKeyboardButton(
                text=category[1],
                callback_data=str(category[1])
            )
        ])
    kb_categories = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb_categories

