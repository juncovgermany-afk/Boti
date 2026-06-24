import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    CallbackQueryHandler,
)

# Включить логирование
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ==================== СОСТОЯНИЯ (States) ====================
(
    WELCOME,
    MAIN_MENU,
    ABOUT,
    CONTACTS,
) = range(4)

# ==================== КЛАВИАТУРЫ ====================

def get_welcome_keyboard():
    """Клавиатура для приветственного сообщения"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Далее", callback_data="next_step")],
        [InlineKeyboardButton("На этом хватит", callback_data="stop")],
    ])

def get_main_menu_keyboard():
    """Главное меню (кнопки-ссылки для сайта и канала)"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Пакеты услуг / их стоимость", callback_data="packages")],
        [InlineKeyboardButton("Наш сайт-визитка", url="https://turbosite.na4u.ru")],
        [InlineKeyboardButton("Наш тг-канал", url="https://t.me/Turbosite_channel")],
        [InlineKeyboardButton("Средства связи со мной", callback_data="contacts")],
        [InlineKeyboardButton("В чём заключается моя работа", callback_data="about")],
        [InlineKeyboardButton("Вернуться к прошлому шагу", callback_data="back_to_welcome")],
    ])

def get_about_keyboard():
    """Клавиатура для сообщения «О себе»"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Средства связи", callback_data="contacts")],
        [InlineKeyboardButton("Меню", callback_data="main_menu")],
    ])

def get_contacts_keyboard():
    """Клавиатура для контактов"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("В меню", callback_data="main_menu")],
    ])

# ==================== ТЕКСТЫ СООБЩЕНИЙ ====================

WELCOME_TEXT = (
    "Приветствую, {username}! Этот бот сделан специально для того, "
    "чтобы вы смогли посмотреть мой готовый продукт в виде данного "
    "чат-бота и его логику действий."
)

MAIN_MENU_TEXT = (
    "В этом меню с кнопками вы можете выбрать интересную для вас информацию."
)

PACKAGES_TEXT = (
    "1. «Рекламный пакет» — от 1500 ₽\n"
    "Что входит:\n"
    "• Помощь с подбором Telegram-каналов и каналов в других "
    "мессенджерах для размещения рекламы\n"
    "• Печать листовок (тираж от 50 шт.)\n"
    "• Расклейка листовок в моём городе и близлежащих городах*\n\n"
    "💬 Цена зависит от тиража и количества городов.\n\n"

    "2. «Минимум» — от 3000 ₽\n"
    "Чат-бот для вашего канала:\n"
    "• Бот-визитка, ведущий в ваш канал в любом мессенджере "
    "(Telegram / WhatsApp / Viber)\n"
    "• Приветствие, кнопки, контакты\n"
    "• Подключение дополнительных мессенджеров (за доплату)\n\n"
    "💬 Базовая цена — 3000 ₽ за одного бота.\n\n"

    "3. «Средний пакет» — от 5000 ₽\n"
    "Чат-бот + привлечение клиентов:\n"
    "• Всё из пакета «Минимум»\n"
    "• Всё из «Рекламного пакета»\n"
    "• Экономия: при заказе вместе — дешевле, чем по отдельности.\n\n"

    "4. «Максимум» — от 8000 ₽\n"
    "Всё включено для старта:\n"
    "• Всё из «Среднего пакета»\n"
    "• Сайт-визитка\n"
    "• 5 блоков: услуги, цены, контакты, форма заявки\n"
    "• Адаптация под телефон"
)

ABOUT_TEXT = (
    "**Чем я занимаюсь и почему это полезно для вас**\n\n"
    "Я создаю цифровые инструменты для малого бизнеса:\n\n"
    "✅ «Сайты-визитки» — чтобы вас находили через поиск и доверяли\n"
    "✅ «Чат-ботов для Telegram, VK» — чтобы отвечать на вопросы "
    "и собирать заявки 24/7\n"
    "✅ «Помощь с рекламой» — подбор каналов, печать и расклейка листовок\n\n"
    "**Почему вам стоит обратиться ко мне?**\n\n"
    "⏱ «Экономия времени» — вы занимаетесь своим делом, а я делаю так, "
    "чтобы клиенты сами вас находили.\n"
    "💰 «Доступные цены» — пакеты от 1500 ₽, без скрытых платежей.\n"
    "🔑 «Под ключ» — я не просто настраиваю, а объясняю, как пользоваться, "
    "и помогаю с запуском.\n\n"
    "**Результат:** ваш бизнес выглядит солидно, работает без выходных "
    "и привлекает больше клиентов.\n\n"
    "💬 Остались вопросы? Нажмите «Средства связи со мной» — я на связи."
)

CONTACTS_TEXT = (
    "Телеграмм: @Maxsimad\n"
    "ВК: Раткогло Максим"
)

# ==================== ОБРАБОТЧИКИ ====================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработчик команды /start"""
    username = update.effective_user.first_name
    text = WELCOME_TEXT.format(username=username)

    await update.message.reply_text(
        text,
        reply_markup=get_welcome_keyboard(),
        parse_mode="HTML",
    )
    return WELCOME

async def welcome_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработчик кнопок приветственного экрана"""
    query = update.callback_query
    await query.answer()

    if query.data == "next_step":
        await query.edit_message_text(
            MAIN_MENU_TEXT,
            reply_markup=get_main_menu_keyboard(),
        )
        return MAIN_MENU

    elif query.data == "stop":
        await query.edit_message_text(
            "Спасибо за внимание! Если захотите узнать больше — просто напишите /start",
        )
        return ConversationHandler.END

    return WELCOME

async def main_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработчик главного меню"""
    query = update.callback_query
    await query.answer()

    if query.data == "packages":
        await query.edit_message_text(
            PACKAGES_TEXT,
            reply_markup=get_main_menu_keyboard(),
            parse_mode="HTML",
        )
        return MAIN_MENU

    elif query.data == "contacts":
        await query.edit_message_text(
            CONTACTS_TEXT,
            reply_markup=get_contacts_keyboard(),
        )
        return CONTACTS

    elif query.data == "about":
        await query.edit_message_text(
            ABOUT_TEXT,
            reply_markup=get_about_keyboard(),
            parse_mode="Markdown",
        )
        return ABOUT

    elif query.data == "back_to_welcome":
        username = update.effective_user.first_name
        text = WELCOME_TEXT.format(username=username)
        await query.edit_message_text(
            text,
            reply_markup=get_welcome_keyboard(),
            parse_mode="HTML",
        )
        return WELCOME

    return MAIN_MENU

async def about_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработчик кнопок на экране «О себе»"""
    query = update.callback_query
    await query.answer()

    if query.data == "contacts":
        await query.edit_message_text(
            CONTACTS_TEXT,
            reply_markup=get_contacts_keyboard(),
        )
        return CONTACTS

    elif query.data == "main_menu":
        await query.edit_message_text(
            MAIN_MENU_TEXT,
            reply_markup=get_main_menu_keyboard(),
        )
        return MAIN_MENU

    return ABOUT

async def contacts_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработчик кнопок на экране контактов"""
    query = update.callback_query
    await query.answer()

    if query.data == "main_menu":
        await query.edit_message_text(
            MAIN_MENU_TEXT,
            reply_markup=get_main_menu_keyboard(),
        )
        return MAIN_MENU

    return CONTACTS

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Отмена диалога"""
    await update.message.reply_text("Диалог завершён. Напишите /start, чтобы начать заново.")
    return ConversationHandler.END

# ==================== ЗАПУСК БОТА ====================

def main():
    TOKEN = os.getenv('BOT_TOKEN')
    if not TOKEN:
        logger.error("BOT_TOKEN не задан!")
        return

    application = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            WELCOME: [CallbackQueryHandler(welcome_handler)],
            MAIN_MENU: [CallbackQueryHandler(main_menu_handler)],
            ABOUT: [CallbackQueryHandler(about_handler)],
            CONTACTS: [CallbackQueryHandler(contacts_handler)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)

    print("Бот запущен...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
