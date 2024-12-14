from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from config import token
import sqlite3, logging, random, asyncio


bot = Bot(token=token)
dp = Dispatcher(storage=MemoryStorage())
router = Router()
dp.include_router(router)
logging.basicConfig(level=logging.INFO)


def generate_personal_code():
    random_number = random.randint(100, 999)
    return f"KRE-{random_number}"


class ClientForm(StatesGroup):
    waiting_for_name = State()
    waiting_for_last_name = State()
    waiting_for_phone = State()


start_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Получить персональный код")]
    ],
    resize_keyboard=True
)


@router.message(F.text == "/start")
async def start_command(message: Message):
    await message.answer(
        "Салемчикивау нажмай на кнопку чтобы начать свой бизнес",
        reply_markup=start_keyboard
    )


@router.message(F.text == "Получить персональный код")
async def handle_get_code(message: Message, state: FSMContext):
    await message.answer("Введи имя:")
    await state.set_state(ClientForm.waiting_for_name)


@router.message(ClientForm.waiting_for_name)
async def get_name(message: Message, state: FSMContext):
    await state.update_data(first_name=message.text)
    await message.answer("Введи фамилию:")
    await state.set_state(ClientForm.waiting_for_last_name)


@router.message(ClientForm.waiting_for_last_name)
async def get_last_name(message: Message, state: FSMContext):
    await state.update_data(last_name=message.text)
    await message.answer("Введи номер тел")
    await state.set_state(ClientForm.waiting_for_phone)


@router.message(ClientForm.waiting_for_phone)
async def get_phone_and_save(message: Message, state: FSMContext):
    user_data = await state.get_data()
    first_name = user_data['first_name']
    last_name = user_data['last_name']
    phone_number = message.text
    if not phone_number.isdigit() or len(phone_number) < 10:
        await message.answer("Неверный формат номера")
        return

    personal_code = generate_personal_code()

    with sqlite3.connect('clients.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            phone_number TEXT NOT NULL,
            personal_code TEXT NOT NULL
        )''')
        conn.commit()

        cursor.execute("INSERT INTO clients (first_name, last_name, phone_number, personal_code) VALUES (?, ?, ?, ?)",
                       (first_name, last_name, phone_number, personal_code))
        conn.commit()

    await message.answer(
        f"Твои данные\n"
        f"Имя {first_name}\n"
        f"Фамилия {last_name}\n"
        f"Телефон {phone_number}\n"
        f"Персональный код {personal_code}\n\n"
        f"Адрес склада Улица пушкина дом колотушкина же есть"
    )
    await state.clear()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
