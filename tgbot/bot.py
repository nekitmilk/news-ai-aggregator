import os
import asyncio
import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

API_URL = os.getenv("API_URL", "http://backend:8000/api/v1")
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN not provided")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ---------------------------
# Храним выбор пользователя
# ---------------------------
user_selected_sources = {}      # user_id -> set(id источников)
user_sources_cache = {}         # user_id -> список источников

user_selected_categories = {}   # user_id -> set(id категорий)
user_categories_cache = {}      # user_id -> список категорий

user_keywords = {}              # user_id -> str
user_waiting_keyword = {}       # user_id -> bool (ожидаем ли ввод ключевого слова)

user_pages = {}                 # user_id -> текущая страница новостей

NEWS_LIMIT = 5  # количество новостей на страницу

# ---------------------------
# Основная Reply-клавиатура
# ---------------------------
def main_reply_keyboard() -> types.ReplyKeyboardMarkup:
    buttons = [
        [types.KeyboardButton(text="Задать фильтры")],
        [types.KeyboardButton(text="Сбросить фильтры")],
        [types.KeyboardButton(text="Получить новости по фильтрам")]
    ]
    return types.ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

# ---------------------------
# Inline-клавиатура для фильтров
# ---------------------------
def filters_inline_keyboard() -> types.InlineKeyboardMarkup:
    buttons = [
        [types.InlineKeyboardButton(text="Выбор источников", callback_data="choose_sources")],
        [types.InlineKeyboardButton(text="Выбор категорий", callback_data="choose_categories")],
        [types.InlineKeyboardButton(text="Задать ключевые слова", callback_data="set_keywords")],
        [types.InlineKeyboardButton(text="Сбросить фильтр по ключевым словам", callback_data="reset_keywords")]
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=buttons)

# ---------------------------
# Inline-клавиатура источников
# ---------------------------
def build_sources_keyboard(user_id: int) -> types.InlineKeyboardMarkup:
    sources = user_sources_cache.get(user_id, [])
    selected = user_selected_sources.get(user_id, set())
    keyboard_buttons = []

    all_selected = len(selected) == len(sources) and len(sources) > 0
    keyboard_buttons.append([types.InlineKeyboardButton(
        text="Снять выделение со всех" if all_selected else "Выбрать все",
        callback_data="toggle_all_sources"
    )])

    for source in sources:
        checked = "✅" if source["id"] in selected else "❌"
        keyboard_buttons.append([types.InlineKeyboardButton(
            text=f"{checked} {source['name']}",
            callback_data=f"source_{source['id']}"
        )])

    keyboard_buttons.append([types.InlineKeyboardButton(text="Готово", callback_data="done_sources")])
    return types.InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)

# ---------------------------
# Inline-клавиатура категорий
# ---------------------------
def build_categories_keyboard(user_id: int) -> types.InlineKeyboardMarkup:
    categories = user_categories_cache.get(user_id, [])
    selected = user_selected_categories.get(user_id, set())
    keyboard_buttons = []

    all_selected = len(selected) == len(categories) and len(categories) > 0
    keyboard_buttons.append([types.InlineKeyboardButton(
        text="Снять выделение со всех" if all_selected else "Выбрать все",
        callback_data="toggle_all_categories"
    )])

    for category in categories:
        checked = "✅" if category["id"] in selected else "❌"
        keyboard_buttons.append([types.InlineKeyboardButton(
            text=f"{checked} {category['name']}",
            callback_data=f"category_{category['id']}"
        )])

    keyboard_buttons.append([types.InlineKeyboardButton(text="Готово", callback_data="done_categories")])
    return types.InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)

# ---------------------------
# Inline-клавиатура "Получить ещё"
# ---------------------------
def more_news_keyboard(page: int = 2) -> types.InlineKeyboardMarkup:
    return types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="Получить ещё", callback_data=f"more_news_{page}")]
    ])

# ---------------------------
# /start
# ---------------------------
@dp.message(Command(commands=["start"]))
async def cmd_start(message: types.Message):
    await message.answer(
        "👋 Привет! Чтобы получать новости по твоим фильтрам или все новости, используй кнопки ниже.",
        reply_markup=main_reply_keyboard()
    )

# ---------------------------
# Нажатие "Задать фильтры"
# ---------------------------
@dp.message(lambda message: message.text == "Задать фильтры")
async def set_filters(message: types.Message):
    await message.answer(
        "Здесь ты можешь задать фильтры для ленты новостей:",
        reply_markup=filters_inline_keyboard()
    )

# ---------------------------
# Нажатие "Сбросить фильтры"
# ---------------------------
@dp.message(lambda message: message.text == "Сбросить фильтры")
async def reset_filters(message: types.Message):
    user_id = message.from_user.id
    user_selected_sources.pop(user_id, None)
    user_selected_categories.pop(user_id, None)
    user_keywords.pop(user_id, None)
    user_waiting_keyword[user_id] = False
    user_pages.pop(user_id, None)
    await message.answer("Все фильтры успешно сброшены. Вы можете задать новые фильтры.")

# ---------------------------
# Нажатие "Получить новости по фильтрам"
# ---------------------------
@dp.message(lambda message: message.text == "Получить новости по фильтрам")
async def get_filtered_news(message: types.Message):
    user_id = message.from_user.id
    await send_news(user_id, message, page=1)

# ---------------------------
# Функция отправки новостей
# ---------------------------
async def send_news(user_id: int, message_or_query, page: int = 1):
    source_ids = ",".join(user_selected_sources.get(user_id, []))
    category_ids = ",".join(user_selected_categories.get(user_id, []))
    search = user_keywords.get(user_id, "").strip()

    params = {"limit": NEWS_LIMIT, "page": page, "sort_order": "desc"}
    if source_ids:
        params["source_ids"] = source_ids
    if category_ids:
        params["category_ids"] = category_ids
    if search:
        params["search"] = search

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(f"{API_URL.rstrip('/')}/news", params=params, timeout=10) as resp:
                data = await resp.json()
                if not data.get("success", True):
                    await message_or_query.answer("Ошибка при получении новостей: " + data.get("message", "Неизвестная ошибка"))
                    return

                news_list = data.get("result", [])
                if not news_list:
                    await message_or_query.answer("Новостей по выбранным фильтрам больше нет.")
                    return

                text_messages = []
                for news in news_list:
                    text_messages.append(
                        f"📌 [{news.get('category','Без категории')}] {news.get('title','Без заголовка')} ({news.get('source','')})\n"
                        f"{news.get('summary','')}\n"
                        f"📅 {news.get('date','')}\n"
                        f"🔗 {news.get('url','')}"
                    )

                user_pages[user_id] = page

                await message_or_query.answer(
                    "\n\n".join(text_messages),
                    reply_markup=more_news_keyboard(page + 1) if len(news_list) == NEWS_LIMIT else None
                )

                if len(news_list) < NEWS_LIMIT:
                    await message_or_query.answer("✅ Это все новости по вашим фильтрам.")
        except Exception as e:
            await message_or_query.answer(f"Ошибка при получении новостей: {e}")

# ---------------------------
# "Получить ещё"
# ---------------------------
@dp.callback_query(lambda c: c.data and c.data.startswith("more_news_"))
async def more_news_callback(query: types.CallbackQuery):
    user_id = query.from_user.id
    page = int(query.data.replace("more_news_", ""))
    await send_news(user_id, query.message, page)
    await query.answer()

# ---------------------------
# Inline callback фильтры
# ---------------------------
@dp.callback_query()
async def process_selection(query: types.CallbackQuery):
    user_id = query.from_user.id
    data = query.data

    # Выбор источников
    if data == "choose_sources":
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(f"{API_URL.rstrip('/')}/sources", timeout=10) as resp:
                    data = await resp.json()
                    sources = data.get("result", [])
                    user_sources_cache[user_id] = sources
                    if user_id not in user_selected_sources or not user_selected_sources[user_id]:
                        user_selected_sources[user_id] = {s["id"] for s in sources}
                    keyboard = build_sources_keyboard(user_id)
                    await query.message.answer("Выберите источники:", reply_markup=keyboard)
                    await query.answer()
            except Exception as e:
                await query.message.answer(f"Ошибка при получении источников: {e}")
                await query.answer()
        return

    # Выбор категорий
    if data == "choose_categories":
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(f"{API_URL.rstrip('/')}/categories", timeout=10) as resp:
                    data = await resp.json()
                    categories = data.get("result", [])
                    user_categories_cache[user_id] = categories
                    if user_id not in user_selected_categories or not user_selected_categories[user_id]:
                        user_selected_categories[user_id] = {c["id"] for c in categories}
                    keyboard = build_categories_keyboard(user_id)
                    await query.message.answer("Выберите категории:", reply_markup=keyboard)
                    await query.answer()
            except Exception as e:
                await query.message.answer(f"Ошибка при получении категорий: {e}")
                await query.answer()
        return

    # Ключевые слова
    if data == "set_keywords":
        user_waiting_keyword[user_id] = True
        await query.message.answer(
            "Введите ключевое слово или фразу для поиска:",
            reply_markup=types.InlineKeyboardMarkup(
                inline_keyboard=[
                    [types.InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_keyword_input")]
                ]
            )
        )
        await query.answer()
        return

    if data == "cancel_keyword_input":
        user_waiting_keyword[user_id] = False
        await query.message.answer("Ввод ключевого слова отменён.", reply_markup=main_reply_keyboard())
        await query.answer()
        return

    if data == "reset_keywords":
        user_keywords.pop(user_id, None)
        user_waiting_keyword[user_id] = False
        await query.message.answer("Фильтр по ключевым словам сброшен.", reply_markup=main_reply_keyboard())
        await query.answer()
        return

    # Источники и категории
    if data.startswith("source_"):
        source_id = data.replace("source_", "")
        selected = user_selected_sources.setdefault(user_id, set())
        if source_id in selected: selected.remove(source_id)
        else: selected.add(source_id)
        await query.message.edit_reply_markup(reply_markup=build_sources_keyboard(user_id))
        await query.answer()
        return

    if data.startswith("category_"):
        category_id = data.replace("category_", "")
        selected = user_selected_categories.setdefault(user_id, set())
        if category_id in selected: selected.remove(category_id)
        else: selected.add(category_id)
        await query.message.edit_reply_markup(reply_markup=build_categories_keyboard(user_id))
        await query.answer()
        return

    if data == "toggle_all_sources":
        sources = user_sources_cache.get(user_id, [])
        if len(user_selected_sources.get(user_id,set())) == len(sources):
            user_selected_sources[user_id] = set()
        else:
            user_selected_sources[user_id] = {s["id"] for s in sources}
        await query.message.edit_reply_markup(reply_markup=build_sources_keyboard(user_id))
        await query.answer()
        return

    if data == "toggle_all_categories":
        categories = user_categories_cache.get(user_id, [])
        if len(user_selected_categories.get(user_id,set())) == len(categories):
            user_selected_categories[user_id] = set()
        else:
            user_selected_categories[user_id] = {c["id"] for c in categories}
        await query.message.edit_reply_markup(reply_markup=build_categories_keyboard(user_id))
        await query.answer()
        return

    if data == "done_sources":
        selected_ids = user_selected_sources.get(user_id, set())
        sources = user_sources_cache.get(user_id, [])
        selected_sources = [s for s in sources if s["id"] in selected_ids]
        if selected_sources:
            text = "\n".join(f"{s['name']} ({s.get('domain','')})" for s in selected_sources)
            await query.message.answer(f"Вы выбрали следующие источники:\n{text}")
        else:
            await query.message.answer("Вы не выбрали ни одного источника.")
        await query.answer()
        return

    if data == "done_categories":
        selected_ids = user_selected_categories.get(user_id, set())
        categories = user_categories_cache.get(user_id, [])
        selected_categories = [c for c in categories if c["id"] in selected_ids]
        if selected_categories:
            text = "\n".join(c['name'] for c in selected_categories)
            await query.message.answer(f"Вы выбрали следующие категории:\n{text}")
        else:
            await query.message.answer("Вы не выбрали ни одной категории.")
        await query.answer()
        return

# ---------------------------
# Обработка текстовых сообщений
# ---------------------------
@dp.message()
async def process_text(message: types.Message):
    user_id = message.from_user.id
    waiting = user_waiting_keyword.get(user_id, False)

    if waiting and message.content_type != "text":
        await message.answer("💬 Пожалуйста, введите текстовое сообщение (ключевое слово или фразу).")
        return

    if message.content_type != "text":
        await message.answer("💡 Для работы с ботом, пожалуйста, используйте кнопки меню ниже 😊")
        return

    text = message.text.strip()

    if text.lower() == "отмена":
        user_waiting_keyword[user_id] = False
        await message.answer("Ввод ключевого слова отменён.", reply_markup=main_reply_keyboard())
        return

    if text in ["Задать фильтры", "Получить новости по фильтрам", "Сбросить фильтры"]:
        return

    if not waiting:
        await message.answer("💡 Для работы с ботом, пожалуйста, используйте кнопки меню ниже 😊")
        return

    user_waiting_keyword[user_id] = False
    user_keywords[user_id] = text
    await message.answer(
        f"🔍 Ключевое слово сохранено:\n<b>{text}</b>",
        parse_mode="HTML",
        reply_markup=main_reply_keyboard()
    )

# ---------------------------
# Запуск
# ---------------------------
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
