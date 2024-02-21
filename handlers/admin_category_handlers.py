from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command

from config import DB_NAME, admins
from keyboards.admin_inline_keyboards import make_category_list
from states.admin_states import CategoryStates
from utils.database import Database
from utils.my_commands import commands_admin, commands_user

category_router = Router()
db = Database(DB_NAME)


@category_router.message(CommandStart())
async def start_handler(message: Message, state: FSMContext):
    await state.clear()
    if message.from_user.id in admins:
        await message.bot.set_my_commands(commands=commands_admin)
        await message.answer("Welcome admin, please choose command from commands list")
    else:
        await message.bot.set_my_commands(commands=commands_user)
        await message.answer("Let's start registration")


@category_router.message(Command('cancel'))
async def cancel_handler(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("All actions canceled, you may continue sending commands")


@category_router.message(Command('categories'))
async def categories_list_handler(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        text="Categories list:",
        reply_markup=make_category_list()
    )


# With this handler admin can add new category
@category_router.message(Command('new_category'))
async def new_category_handler(message: Message, state: FSMContext):
    await state.set_state(CategoryStates.newCategory_state)
    await message.answer("Please, send new category name ...")


@category_router.message(CategoryStates.newCategory_state)
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


# Functions for editing category name
@category_router.message(Command('edit_category'))
async def edit_category_handler(message: Message, state: FSMContext):
    await state.set_state(CategoryStates.updCategory_state_list)
    await message.answer(
        text="Choose category name which you want to change...",
        reply_markup=make_category_list()
    )


@category_router.callback_query(CategoryStates.updCategory_state_list)
async def callback_category_edit(callback: CallbackQuery, state: FSMContext):
    await state.update_data(cat_name=callback.data)
    await state.set_state(CategoryStates.updCategory_state_new)
    await callback.message.answer(f"Please, send new name for category '{callback.data}'")
    await callback.message.delete()


@category_router.message(CategoryStates.updCategory_state_new)
async def set_new_category_name(message: Message, state: FSMContext):
    new_cat = message.text
    st_data = await state.get_data()
    old_cat = st_data.get('cat_name')
    res = db.upd_category(message.text, old_cat)
    if res['status']:
        await message.answer("Category name successfully changed")
        await state.clear()
    elif res['desc'] == 'exists':
        await message.reply("This category already exists.\n"
                            "Please, send other name or click /cancel")
    else:
        await message.reply(res['desc'])


@category_router.message(Command('del_category'))
async def del_category_handler(message: Message, state: FSMContext):
    await state.set_state(CategoryStates.delCategory_state)
    await message.answer(
        text="Choose category name which you want to delete...",
        reply_markup=make_category_list()
    )


@category_router.callback_query(CategoryStates.delCategory_state)
async def callback_category_delete(callback: CallbackQuery, state: FSMContext):
    if db.del_category(cat_name=callback.data):
        await state.clear()
        await callback.message.edit_text(f"Category with name '{callback.data}' successfully deleted")
    else:
        await callback.message.answer(f"Something error, please, try again!")
