import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message
from config import BOT_TOKEN
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

GOODS = {
    "1": {"name": "Шорты 🩳", "price": 1500, "desc": "Летние, хлопок, 3 цвета"},
    "2": {"name": "Футболка 👕", "price": 2000, "desc": "Премиум качество, принт"},
    "3": {"name": "Кепка 🧢", "price": 1200, "desc": "Регулируемая, защита от солнца"},
}


@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        f"👋 Привет, {message.from_user.full_name}!\n"
        "Я готов к работе. Используй /help для списка команд."
    )


@dp.message(F.text == "Привет")
async def hello_handler(message: Message):
    await message.answer("Привет в ответ! 🙌")


@dp.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        f"{message.from_user.first_name}, я умею отвечать на 'Привет'\n"
        "Просто введи Привет и я отвечу",
        reply_markup=get_test_keyboard()
    )


@dp.callback_query(F.data == "btn_test")
async def process_test_callback(callback: CallbackQuery):
    await callback.answer("✅ Кнопка нажата!", show_alert=False)

    await callback.message.edit_text(
        f"🎉 {callback.from_user.first_name}, ты нажал кнопку!\n"
        "Теперь можно вернуться назад.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Назад", callback_data="btn_back")]
        ])
    )


@dp.callback_query(F.data == "btn_back")
async def process_back_callback(callback: CallbackQuery):
    await callback.answer()  # пустой ответ — тоже валидный
    await callback.message.edit_text(
        f"{callback.from_user.first_name}, я умею отвечать на 'Привет'\n"
        "Просто введи Привет и я отвечу",
        reply_markup=get_test_keyboard()
    )


def get_test_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔔 Нажми меня", callback_data="btn_test"),
         InlineKeyboardButton(text="📦 Товары", callback_data="btn_goods")]
    ])
    return keyboard


def get_goods_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"{data['name']} — {data['price']}₽",
                             callback_data=f"view:{item_id}")]
        for item_id, data in GOODS.items()
    ])
    keyboard.inline_keyboard.append(
        [InlineKeyboardButton(text="🔙 Назад", callback_data="menu:back")]
    )
    return keyboard


@dp.callback_query(F.data == "btn_goods")
async def show_goods(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer(
        text="Доступные товары:",
        reply_markup=get_goods_keyboard()
    )


@dp.callback_query(F.data.startswith("view:"))
async def view_item(callback: CallbackQuery):
    item_id = callback.data.split(":")[1]
    item = GOODS.get(item_id)

    if not item:
        await callback.answer("❌ Товар не найден", show_alert=True)
        return

    await callback.answer()
    await callback.message.edit_text(
        f"<b>{item['name']}</b>\n"
        f"💰 Цена: {item['price']}₽\n"
        f"📝 {item['desc']}\n",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Купить", callback_data=f"buy:{item_id}")],
            [InlineKeyboardButton(text="📦 Все товары", callback_data="menu:goods"),
             InlineKeyboardButton(text="🔙 Назад", callback_data="menu:back")]
        ])
    )


@dp.callback_query(F.data.startswith("buy"))
async def process_purchase(callback: CallbackQuery):
    await callback.answer()
    item_id = callback.data.split(":")[1]
    item = GOODS.get(item_id)
    if not item:
        await callback.message.answer("❌ Товар не найден", show_alert=True)
        return

    await callback.message.edit_text(
        f"<b>{item['name']}</b>\n"
        f"💰 Цена: {item['price']}₽\n"
        f"📝 {item['desc']}\n"
        "🧺 Товар добален в корзину\n",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📦 Все товары", callback_data="menu:goods"),
             InlineKeyboardButton(text="🔙 Назад", callback_data="menu:back")]
        ])
    )


@dp.callback_query(F.data.startswith("menu"))
async def menu_actions(callback: CallbackQuery):
    await callback.answer()
    action = callback.data.split(":")[1]

    if action == "goods":
        await callback.message.answer(
            text="Доступные товары:",
            reply_markup=get_goods_keyboard()
        )
    if action == "back":
        await callback.message.answer(
            text="Окей, возвращаемся назад",
            reply_markup=get_test_keyboard()
        )


async def main():
    logging.info("Запуск бота...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
