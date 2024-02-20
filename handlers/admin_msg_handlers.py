from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from config import DB_NAME
from states.admin_states import CategoryStates
from utils.database import Database

admin_message_router = Router()
db = Database(DB_NAME)


@admin_message_router.message(CategoryStates.newCategory_state)
async def new_category_handler(message: Message, state: FSMContext):
    res = db.add_category(message.text)
    if res['status']:
        await message.answer("New category successfully added")
        await state.clear()
    elif res['desc'] == 'exists':
        await message.reply("This category already exists.\n"
                            "Please, send other name or click /cancel")
    else:
        await message.reply(res['desc'])

