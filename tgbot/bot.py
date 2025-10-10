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

def ensure_user_initialized(user_id: int):
    """Гарантирует, что у пользователя есть все нужные записи в памяти."""
    user_selected_sources.setdefault(user_id, set())
    user_sources_cache.setdefault(user_id, [])
    user_selected_categories.setdefault(user_id, set())
    user_categories_cache.setdefault(user_id, [])
    user_keywords.setdefault(user_id, "")
    user_waiting_keyword.setdefault(user_id, False)
    user_pages.setdefault(user_id, 1)

# ---------------------------
# Основная Reply-клавиатура
# ---------------------------
def main_reply_keyboard() -> types.ReplyKeyboardMarkup:
    buttons = [
        [types.KeyboardButton(text="Задать фильтры")],
        [types.KeyboardButton(text="Получить новости по фильтрам")],
        [types.KeyboardButton(text="Получить персонализированные новости")]
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
        [types.InlineKeyboardButton(text="Сбросить все фильтры", callback_data="reset_all_filters")],
        [types.InlineKeyboardButton(text="Сохранить фильтры", callback_data="save_filters")],
        [types.InlineKeyboardButton(text="Использовать сохранённые фильтры", callback_data="get_saved_filters")]
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=buttons)
# ---------------------------
# Inline-клавиатура источников
# ---------------------------
def build_sources_keyboard(user_id: int) -> types.InlineKeyboardMarkup:
    sources = user_sources_cache.get(user_id, [])
    selected = user_selected_sources.get(user_id, set())
    keyboard_buttons = []

    # Кнопка "Выбрать все / Снять выделение со всех"
    all_selected = len(selected) == len(sources) and len(sources) > 0
    keyboard_buttons.append([types.InlineKeyboardButton(
        text="Снять выделение со всех" if all_selected else "Выбрать все",
        callback_data="toggle_all_sources"
    )])

    # Кнопки источников по 2 в ряд
    row = []
    for source in sources:
        checked = "✅" if source["id"] in selected else "❌"
        btn = types.InlineKeyboardButton(
            text=f"{checked} {source['name']}",
            callback_data=f"source_{source['id']}"
        )
        row.append(btn)
        if len(row) == 2:
            keyboard_buttons.append(row)
            row = []
    if row:  # добавляем остаток, если число источников нечётное
        keyboard_buttons.append(row)
    # Кнопка "Готово"
    keyboard_buttons.append([types.InlineKeyboardButton(text="Готово", callback_data="done_sources")])
    return types.InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)


# ---------------------------
# Inline-клавиатура категорий
# ---------------------------
def build_categories_keyboard(user_id: int) -> types.InlineKeyboardMarkup:
    categories = user_categories_cache.get(user_id, [])
    selected = user_selected_categories.get(user_id, set())
    keyboard_buttons = []

    # Кнопка "Выбрать все / Снять выделение со всех"
    all_selected = len(selected) == len(categories) and len(categories) > 0
    keyboard_buttons.append([types.InlineKeyboardButton(
        text="Снять выделение со всех" if all_selected else "Выбрать все",
        callback_data="toggle_all_categories"
    )])

    # Кнопки категорий по 2 в ряд
    row = []
    for category in categories:
        checked = "✅" if category["id"] in selected else "❌"
        btn = types.InlineKeyboardButton(
            text=f"{checked} {category['name']}",
            callback_data=f"category_{category['id']}"
        )
        row.append(btn)
        if len(row) == 2:
            keyboard_buttons.append(row)
            row = []
    if row:  # добавляем остаток, если число категорий нечётное
        keyboard_buttons.append(row)

    # Кнопка "Готово"
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
    user_id = message.from_user.id
    ensure_user_initialized(user_id)

    # --- Проверяем, есть ли сохранённые фильтры в бэкенде ---
    async with aiohttp.ClientSession() as session:
        headers = {"X-User-ID": str(user_id)}
        try:
            async with session.get(f"{API_URL.rstrip('/')}/users/filters/{user_id}", headers=headers, timeout=10) as resp:
                data = await resp.json()
                if resp.status != 200 or not data.get("success", True):
                    # Если фильтров нет, создаём запись с пустыми фильтрами
                    payload = {
                        "source": [],
                        "category": [],
                        "search": None,
                        "start_date": None,
                        "end_date": None,
                        "sort": "desc"
                    }
                    try:
                        async with session.post(f"{API_URL.rstrip('/')}/users/filters/", json=payload, headers=headers, timeout=10) as post_resp:
                            # не проверяем результат — делаем тихо
                            await post_resp.json()
                    except Exception:
                        pass  # игнорируем ошибки
        except Exception:
            pass  # игнорируем ошибки

    # --- Основной стартовый текст и клавиатура ---
    await message.answer(
        "👋 Привет! Чтобы получать новости по твоим фильтрам или все новости, используй кнопки ниже.",
        reply_markup=main_reply_keyboard()
    )


# ---------------------------
# Нажатие "Задать фильтры"
# ---------------------------
@dp.message(lambda message: message.text == "Задать фильтры")
async def set_filters(message: types.Message):
    user_id = message.from_user.id
    ensure_user_initialized(user_id)
    await message.answer(
        "Здесь ты можешь задать фильтры для ленты новостей:",
        reply_markup=filters_inline_keyboard()
    )

# ---------------------------
# Нажатие "Получить новости по фильтрам"
# ---------------------------
@dp.message(lambda message: message.text == "Получить новости по фильтрам")
async def get_filtered_news(message: types.Message):
    user_id = message.from_user.id
    ensure_user_initialized(user_id)
    await send_news(user_id, message, page=1)

# ---------------------------
# Функция сохранения фильтровв пользователя
# ---------------------------
async def save_filters_to_backend(user_id: int):
    # Конвертируем ID в int
    sources = [int(s) for s in user_selected_sources.get(user_id, [])]
    categories = [int(c) for c in user_selected_categories.get(user_id, [])]
    keyword = user_keywords.get(user_id, None)

    payload = {
        "source": sources,          # список int
        "category": categories,     # список int
        "search": keyword or None,  # ключевое слово
        "start_date": None,         # можно добавить при необходимости
        "end_date": None,           # можно добавить при необходимости
        "sort": "desc"              # сортировка
    }

    headers = {"X-User-ID": str(user_id)}

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(f"{API_URL.rstrip('/')}/users/filters/", json=payload, headers=headers, timeout=10) as resp:
                data = await resp.json()
                if resp.status != 200 or not data.get("success", True):
                    return False, data.get("message", "Ошибка при сохранении фильтров")
                return True, "Фильтры успешно сохранены"
        except Exception as e:
            return False, str(e)
# ---------------------------
# Функция для получения фильтров источника
# ---------------------------
async def get_saved_filters(user_id: int):
    headers = {"X-User-ID": str(user_id)}

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(f"{API_URL.rstrip('/')}/users/filters/{user_id}", headers=headers, timeout=10) as resp:
                data = await resp.json()
                if resp.status != 200 or not data.get("success", True):
                    return None, data.get("message", "Не удалось получить фильтры")
                
                result = data.get("result", {})

                # Приводим ID к str для согласованности с callback_data
                sources = [str(s) for s in result.get("source", [])]
                categories = [str(c) for c in result.get("category", [])]
                search = result.get("search") or None

                return {"source": sources, "category": categories, "search": search}, "Фильтры успешно получены"
        except Exception as e:
            return None, str(e)

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

                user_pages[user_id] = page

                # Отправляем новости по одной
                for news in news_list:
                    await message_or_query.answer(
                        f"📌 [{news.get('category','Без категории')}] {news.get('title','Без заголовка')} ({news.get('source','')})\n"
                        f"{news.get('summary','')}\n"
                        f"📅 {news.get('date','')}\n"
                        f"🔗 {news.get('url','')}"
                    )

                # Если новостей меньше лимита, информируем пользователя
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

    # Отправляем новости отдельными сообщениями
    await send_news(user_id, query.message, page)

    # Отправляем кнопку "Получить ещё" отдельным сообщением
    await query.message.answer(
        "Нажмите, чтобы получить ещё:",
        reply_markup=more_news_keyboard(page + 1)
    )

    # Закрываем callback
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
        current_keyword = user_keywords.get(user_id)
        current_text = f"\n\n🔹 Текущее ключевое слово: <b>{current_keyword}</b>" if current_keyword else "\n\n🔹 Текущее ключевое слово: не задано"
        
        sent_msg = await query.message.answer(
            f"Введите новое ключевое слово или фразу для поиска:{current_text}",
            parse_mode="HTML",
            reply_markup=types.InlineKeyboardMarkup(
                inline_keyboard=[
                    [types.InlineKeyboardButton(text="Отмена", callback_data="cancel_keyword_input")],
                    [types.InlineKeyboardButton(text="Сбросить ключевое слово", callback_data="reset_keywords")],
                ]
            )
        )

        # сохраняем id сообщения, чтобы потом удалить
        user_waiting_keyword[user_id] = sent_msg.message_id
        await query.answer()
        return


    if data == "cancel_keyword_input":
        user_waiting_keyword[user_id] = False

        # Удаляем сообщение с кнопкой "Отмена" (само сообщение бота)
        try:
            await query.message.delete()
        except Exception:
            pass

        # Определяем текущее ключевое слово (если было ранее)
        current_keyword = user_keywords.get(user_id)
        if current_keyword:
            text = f"❌ Ввод ключевого слова отменён.\n🔹 Текущее ключевое слово: <b>{current_keyword}</b>"
        else:
            text = "❌ Ввод ключевого слова отменён.\n🔹 Ключевое слово не задано."

        await query.message.answer(text, parse_mode="HTML", reply_markup=main_reply_keyboard())
        await query.answer()
        return

    if data == "reset_keywords":
        # Удаляем сообщение бота с просьбой ввести ключевое слово
        waiting_msg_id = user_waiting_keyword.get(user_id)
        if waiting_msg_id:
            try:
                await bot.delete_message(user_id, waiting_msg_id)
            except Exception:
                pass

        user_keywords.pop(user_id, None)
        user_waiting_keyword[user_id] = False
        # Удаляем сообщение пользователя с командой сброса, если есть
        # (это можно сделать, если сброс происходит через текст, иначе оставляем)
        await query.message.answer("✅ Ключевое слово сброшено.", reply_markup=main_reply_keyboard())
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
        await query.message.delete()  # Удаляем сообщение с кнопками
        selected_ids = user_selected_sources.get(user_id, set())
        sources = user_sources_cache.get(user_id, [])
        total = len(sources)
        selected_count = len(selected_ids)

        if selected_count == 0 or selected_count == total:
            await query.message.answer("✅ Вы выбрали все источники.")
        else:
            await query.message.answer(f"✅ Вы выбрали {selected_count} из {total} источников.")
        await query.answer()
        return

    if data == "done_categories":
        await query.message.delete()  # Удаляем сообщение с кнопками
        selected_ids = user_selected_categories.get(user_id, set())
        categories = user_categories_cache.get(user_id, [])
        total = len(categories)
        selected_count = len(selected_ids)

        if selected_count == 0 or selected_count == total:
            await query.message.answer("✅ Вы выбрали все категории.")
        else:
            await query.message.answer(f"✅ Вы выбрали {selected_count} из {total} категорий.")
        await query.answer()
        return
    
    # сбросить фильтры
    if data == "reset_all_filters":
        user_selected_sources.pop(user_id, None)
        user_selected_categories.pop(user_id, None)
        user_keywords.pop(user_id, None)
        user_waiting_keyword[user_id] = False
        user_pages.pop(user_id, None)
        await query.message.answer("✅ Все фильтры успешно сброшены.")
        await query.answer()
        return
    # Сохранить фильтры
    if data == "save_filters":
        success, msg = await save_filters_to_backend(user_id)
        await query.message.answer(
            f"{'✅' if success else '❌'} {msg}",
            reply_markup=main_reply_keyboard()
        )
        await query.answer()
        return
    
    # Получить сохранённые фильтры
    if data == "get_saved_filters":
        filters, msg = await get_saved_filters(user_id)
        
        if not filters:
            await query.message.answer(f"❌ {msg}")
            await query.answer()
            return

        user_selected_sources[user_id] = set(filters["source"])
        user_selected_categories[user_id] = set(filters["category"])
        user_keywords[user_id] = filters["search"]

        sources = filters.get("source", [])
        categories = filters.get("category", [])
        search = filters.get("search", "не задано")

        text = (
            f"📌 Ваши сохранённые фильтры:\n"
            f"Источники: {len(sources)} выбранных\n"
            f"Категории: {len(categories)} выбранных\n"
            f"Ключевое слово: {search}"
        )

        await query.message.answer(text, reply_markup=main_reply_keyboard())
        await query.answer()
        return
# ---------------------------
# Обработка получеия сохраненных фильтров
# ---------------------------
@dp.message(lambda message: message.text == "Получить сохранённые фильтры")
async def show_saved_filters(message: types.Message):
    user_id = message.from_user.id
    filters, msg = await get_saved_filters(user_id)
    
    if not filters:
        await message.answer(f"❌ {msg}")
        return

    # Сохраняем в локальные словари для использования в кнопках и отправки новостей
    user_selected_sources[user_id] = set(filters["source"])
    user_selected_categories[user_id] = set(filters["category"])
    user_keywords[user_id] = filters["search"]

    sources = filters.get("source", [])
    categories = filters.get("category", [])
    search = filters.get("search", "не задано")

    text = (
        f"📌 Ваши сохранённые фильтры:\n"
        f"Источники: {len(sources)} выбранных\n"
        f"Категории: {len(categories)} выбранных\n"
        f"Ключевое слово: {search}"
    )

    await message.answer(text, reply_markup=main_reply_keyboard())

# ---------------------------
# Получить персонализированные новости
# ---------------------------
@dp.message(lambda message: message.text and "персонализированные" in message.text.lower())
async def get_personalized_news(message: types.Message):
    user_id = message.from_user.id
    ensure_user_initialized(user_id)
    page = user_pages.get(user_id, 1)
    await send_personalized_news(user_id, message, page=page)


# ---------------------------
# Функция отправки персонализированных новостей
# ---------------------------
async def send_personalized_news(user_id: int, message_or_query, page: int = 1):
    params = {
        "user_id": user_id,
        "limit": NEWS_LIMIT,
        "page": page
    }

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(f"{API_URL.rstrip('/')}/news/recommendations", params=params, timeout=10) as resp:
                data = await resp.json()

                if not data.get("success", True):
                    await message_or_query.answer("❌ Ошибка при получении персонализированных новостей: " + data.get("message", "Неизвестная ошибка"))
                    return

                news_list = data.get("result", [])
                if not news_list:
                    # вместо ответа просто вызываем send_news без фильтров
                    await send_news(user_id, message_or_query, page=1)
                    return

                user_pages[user_id] = page

                # Отправляем новости
                for news in news_list:
                    await message_or_query.answer(
                        f"📌 [{news.get('category', 'Без категории')}] {news.get('title', 'Без заголовка')} ({news.get('source', '')})\n"
                        f"{news.get('summary', '')}\n"
                        f"📅 {news.get('date', '')}\n"
                        f"🔗 {news.get('url', '')}"
                    )

                # Если есть ещё — предлагаем подгрузить
                if len(news_list) >= NEWS_LIMIT:
                    await message_or_query.answer(
                        "Нажмите, чтобы получить ещё персонализированные новости:",
                        reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
                            [types.InlineKeyboardButton(text="Получить ещё", callback_data=f"more_personal_{page + 1}")]
                        ])
                    )
                else:
                    await message_or_query.answer("✅ Это все персонализированные новости.")
        except Exception as e:
            await message_or_query.answer(f"❌ Ошибка при получении персонализированных новостей: {e}")


# ---------------------------
# Callback "Получить ещё" для персонализированных новостей
# ---------------------------
@dp.callback_query(lambda c: c.data and c.data.startswith("more_personal_"))
async def more_personal_news_callback(query: types.CallbackQuery):
    user_id = query.from_user.id
    page = int(query.data.replace("more_personal_", ""))

    await send_personalized_news(user_id, query.message, page)
    await query.answer()
# ---------------------------
# Обработка текстовых сообщений
# ---------------------------
@dp.message()
async def process_text(message: types.Message):
    user_id = message.from_user.id
    ensure_user_initialized(user_id)
    waiting = user_waiting_keyword.get(user_id, False)

    # Если бот ждёт ключевое слово, но пришло не текстовое сообщение
    if waiting and message.content_type != "text":
        await message.answer("💬 Пожалуйста, введите текстовое сообщение (ключевое слово или фразу).")
        return

    # Если сообщение не текстовое — просто подсказываем
    if message.content_type != "text":
        await message.answer("💡 Для работы с ботом, пожалуйста, используйте кнопки меню ниже 😊")
        return

    text = message.text.strip()

    # --- Обработка отмены ---
    if text.lower() == "отмена":
        user_waiting_keyword[user_id] = False

        # Удаляем последнее сообщение бота с запросом ключевого слова
        try:
            async for msg in bot.get_chat_history(user_id, limit=5):
                if msg.from_user.id == bot.id and "Введите ключевое слово" in msg.text:
                    await bot.delete_message(user_id, msg.message_id)
                    break
        except Exception:
            pass

        # Удаляем сообщение пользователя "отмена"
        try:
            await message.delete()
        except Exception:
            pass

        # Получаем текущее ключевое слово, если было
        current_keyword = user_keywords.get(user_id)
        if current_keyword:
            text_to_send = f"❌ Ввод ключевого слова отменён.\n🔹 Текущее ключевое слово: <b>{current_keyword}</b>"
        else:
            text_to_send = "❌ Ввод ключевого слова отменён.\n🔹 Ключевое слово не задано."

        await message.answer(text_to_send, parse_mode="HTML", reply_markup=main_reply_keyboard())
        return

    # --- Игнорируем кнопки из главного меню ---
    if text in ["Задать фильтры", "Получить новости по фильтрам", "Сбросить фильтры"]:
        return

# --- Если бот ждёт ввод ключевого слова ---
    if waiting:
        user_waiting_keyword[user_id] = False

        # Удаляем предыдущее сообщение бота с просьбой ввести ключевое слово
        try:
            await bot.delete_message(user_id, waiting)  # user_waiting_keyword[user_id] хранит message_id бота
        except Exception:
            pass

        # Удаляем сообщение пользователя с введённым словом
        try:
            await message.delete()
        except Exception:
            pass

        if not text:
            await message.answer("⚠️ Пожалуйста, введи текстовое ключевое слово.", reply_markup=main_reply_keyboard())
            return

        # Сохраняем ключевое слово
        user_keywords[user_id] = text

        # Подтверждение
        await message.answer(
            f"✅ Ключевое слово сохранено: <b>{text}</b>",
            parse_mode="HTML",
            reply_markup=main_reply_keyboard()
        )
        return


    # --- Если бот не ждёт никакого ввода ---
    await message.answer("💡 Для работы с ботом, пожалуйста, используйте кнопки меню ниже 😊")



# ---------------------------
# Запуск
# ---------------------------
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())