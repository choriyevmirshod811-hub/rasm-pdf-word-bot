import os
import re
import shutil
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)
from PIL import Image
from docx import Document
from docx.shared import Inches

TOKEN = os.getenv("8290808043:AAEWX_oDghVc0teDOgJbYVNjnnLXqXdCYmg")

user_images = {}
user_languages = {}
user_pdf_sizes = {}
user_waiting_for_name = {}
user_file_names = {}

texts = {
    "uz": {
        "choose_lang": "Tilni tanlang / Choose language / Выберите язык 👇",
        "welcome": "Til tanlandi ✅\n\nRasm yuboring 👇",
        "send_photo": "Rasm yuboring 📸",
        "photo_saved": "✅ {count} ta rasm qabul qilindi.",
        "no_images": "❌ Rasm yo‘q.",
        "cleared": "🧹 Tozalandi.",
        "help": "Rasm yuboring, keyin kerakli tugmani bosing.",
        "pdf_ready": "✅ PDF tayyor.",
        "word_ready": "✅ Word tayyor.",
        "choose_size": "PDF hajmini tanlang 👇",
        "size_saved": "✅ PDF hajmi saqlandi.",
        "pdf_btn": "📄 PDF qilish",
        "word_btn": "📝 Word qilish",
        "clear_btn": "🧹 Tozalash",
        "help_btn": "ℹ️ Yordam",
        "lang_btn": "🌐 Til",
        "size_btn": "📉 PDF hajmi",
        "size_1": "1 MB",
        "size_2": "2 MB",
        "size_5": "5 MB",
        "size_original": "Original",
        "ask_name_pdf": "PDF fayl nomini yuboring.\nMasalan: fizika_uy_ishi",
        "ask_name_word": "Word fayl nomini yuboring.\nMasalan: fizika_uy_ishi",
        "loading_pdf": "⏳ PDF tayyorlanmoqda...",
        "loading_word": "⏳ Word tayyorlanmoqda...",
        "name_saved_pdf": "✅ Nomi saqlandi. PDF tayyorlayapman...",
        "name_saved_word": "✅ Nomi saqlandi. Word tayyorlayapman...",
        "name_too_long": "❌ Nomi juda uzun. Qisqaroq nom yuboring.",
        "name_empty": "❌ To‘g‘ri nom yuboring.",
    },
    "ru": {
        "choose_lang": "Выберите язык / Choose language / Tilni tanlang 👇",
        "welcome": "Язык выбран ✅\n\nОтправьте фото 👇",
        "send_photo": "Отправьте фото 📸",
        "photo_saved": "✅ Получено фото: {count}.",
        "no_images": "❌ Фото нет.",
        "cleared": "🧹 Очищено.",
        "help": "Отправьте фото, потом нажмите нужную кнопку.",
        "pdf_ready": "✅ PDF готов.",
        "word_ready": "✅ Word готов.",
        "choose_size": "Выберите размер PDF 👇",
        "size_saved": "✅ Размер PDF сохранён.",
        "pdf_btn": "📄 Сделать PDF",
        "word_btn": "📝 Сделать Word",
        "clear_btn": "🧹 Очистить",
        "help_btn": "ℹ️ Помощь",
        "lang_btn": "🌐 Язык",
        "size_btn": "📉 Размер PDF",
        "size_1": "1 MB",
        "size_2": "2 MB",
        "size_5": "5 MB",
        "size_original": "Original",
        "ask_name_pdf": "Отправьте имя PDF файла.\nНапример: fizika_uy_ishi",
        "ask_name_word": "Отправьте имя Word файла.\nНапример: fizika_uy_ishi",
        "loading_pdf": "⏳ PDF создаётся...",
        "loading_word": "⏳ Word создаётся...",
        "name_saved_pdf": "✅ Имя сохранено. Создаю PDF...",
        "name_saved_word": "✅ Имя сохранено. Создаю Word...",
        "name_too_long": "❌ Имя слишком длинное. Отправьте короче.",
        "name_empty": "❌ Отправьте правильное имя.",
    },
    "en": {
        "choose_lang": "Choose language / Tilni tanlang / Выберите язык 👇",
        "welcome": "Language selected ✅\n\nSend images 👇",
        "send_photo": "Send images 📸",
        "photo_saved": "✅ {count} image(s) received.",
        "no_images": "❌ No images.",
        "cleared": "🧹 Cleared.",
        "help": "Send images, then press the needed button.",
        "pdf_ready": "✅ PDF is ready.",
        "word_ready": "✅ Word is ready.",
        "choose_size": "Choose PDF size 👇",
        "size_saved": "✅ PDF size saved.",
        "pdf_btn": "📄 Make PDF",
        "word_btn": "📝 Make Word",
        "clear_btn": "🧹 Clear",
        "help_btn": "ℹ️ Help",
        "lang_btn": "🌐 Language",
        "size_btn": "📉 PDF size",
        "size_1": "1 MB",
        "size_2": "2 MB",
        "size_5": "5 MB",
        "size_original": "Original",
        "ask_name_pdf": "Send the PDF file name.\nExample: physics_homework",
        "ask_name_word": "Send the Word file name.\nExample: physics_homework",
        "loading_pdf": "⏳ Creating PDF...",
        "loading_word": "⏳ Creating Word...",
        "name_saved_pdf": "✅ Name saved. Creating PDF...",
        "name_saved_word": "✅ Name saved. Creating Word...",
        "name_too_long": "❌ Name is too long. Send a shorter one.",
        "name_empty": "❌ Send a valid file name.",
    }
}


def get_user_folder(user_id: int) -> str:
    folder = f"images/{user_id}"
    os.makedirs(folder, exist_ok=True)
    return folder


def get_temp_folder(user_id: int) -> str:
    folder = f"images/{user_id}/temp"
    os.makedirs(folder, exist_ok=True)
    return folder


def get_user_language(user_id: int) -> str:
    return user_languages.get(user_id, "uz")


def get_pdf_quality(size_choice: str) -> int:
    if size_choice == "1":
        return 20
    if size_choice == "2":
        return 35
    if size_choice == "5":
        return 55
    return 95


def sanitize_filename(name: str) -> str:
    name = name.strip()
    name = re.sub(r'[\\/:*?"<>|]+', "", name)
    name = re.sub(r"\s+", "_", name)
    return name


def get_main_menu(lang: str) -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(texts[lang]["pdf_btn"], callback_data="make_pdf"),
            InlineKeyboardButton(texts[lang]["word_btn"], callback_data="make_word"),
        ],
        [
            InlineKeyboardButton(texts[lang]["size_btn"], callback_data="choose_size"),
        ],
        [
            InlineKeyboardButton(texts[lang]["help_btn"], callback_data="help"),
            InlineKeyboardButton(texts[lang]["lang_btn"], callback_data="change_lang"),
        ],
        [
            InlineKeyboardButton(texts[lang]["clear_btn"], callback_data="clear_files"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_language_menu() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("🇺🇿 O'zbek", callback_data="lang_uz")],
        [InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru")],
        [InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_size_menu(lang: str) -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(texts[lang]["size_1"], callback_data="size_1"),
            InlineKeyboardButton(texts[lang]["size_2"], callback_data="size_2"),
        ],
        [
            InlineKeyboardButton(texts[lang]["size_5"], callback_data="size_5"),
            InlineKeyboardButton(texts[lang]["size_original"], callback_data="size_org"),
        ],
        [
            InlineKeyboardButton("⬅️ Back", callback_data="back_main"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def cleanup_temp_folder(user_id: int):
    temp_folder = f"images/{user_id}/temp"
    if os.path.exists(temp_folder):
        shutil.rmtree(temp_folder, ignore_errors=True)


def prepare_images_for_pdf(user_id: int, size_choice: str):
    original_paths = user_images.get(user_id, [])
    temp_paths = []

    if size_choice == "org":
        return original_paths

    quality = get_pdf_quality(size_choice)
    temp_folder = get_temp_folder(user_id)

    for i, path in enumerate(original_paths, start=1):
        img = Image.open(path).convert("RGB")
        temp_path = os.path.join(temp_folder, f"compressed_{i}.jpg")
        img.save(temp_path, "JPEG", quality=quality, optimize=True)
        img.close()
        temp_paths.append(temp_path)

    return temp_paths


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        texts["uz"]["choose_lang"],
        reply_markup=get_language_menu()
    )


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.photo:
        return

    user_id = update.message.from_user.id
    lang = get_user_language(user_id)
    folder = get_user_folder(user_id)

    if user_id not in user_images:
        user_images[user_id] = []

    photo = update.message.photo[-1]
    tg_file = await context.bot.get_file(photo.file_id)

    file_path = os.path.join(folder, f"{photo.file_id}.jpg")
    await tg_file.download_to_drive(file_path)

    user_images[user_id].append(file_path)
    count = len(user_images[user_id])

    await update.message.reply_text(
        texts[lang]["photo_saved"].format(count=count),
        reply_markup=get_main_menu(lang)
    )


async def make_pdf(query, user_id: int, file_name: str):
    lang = get_user_language(user_id)

    if user_id not in user_images or len(user_images[user_id]) == 0:
        await query.message.reply_text(texts[lang]["no_images"])
        return

    loading_msg = await query.message.reply_text(texts[lang]["loading_pdf"])

    size_choice = user_pdf_sizes.get(user_id, "org")
    cleanup_temp_folder(user_id)
    image_paths = prepare_images_for_pdf(user_id, size_choice)

    images = []
    for path in image_paths:
        img = Image.open(path).convert("RGB")
        images.append(img)

    folder = get_user_folder(user_id)
    pdf_path = os.path.join(folder, f"{file_name}.pdf")

    images[0].save(pdf_path, save_all=True, append_images=images[1:])

    for img in images:
        img.close()

    with open(pdf_path, "rb") as f:
        await query.message.reply_document(
            document=f,
            filename=f"{file_name}.pdf",
            caption=texts[lang]["pdf_ready"]
        )

    cleanup_temp_folder(user_id)
    await loading_msg.delete()


async def make_word(query, user_id: int, file_name: str):
    lang = get_user_language(user_id)

    if user_id not in user_images or len(user_images[user_id]) == 0:
        await query.message.reply_text(texts[lang]["no_images"])
        return

    loading_msg = await query.message.reply_text(texts[lang]["loading_word"])

    folder = get_user_folder(user_id)
    doc_path = os.path.join(folder, f"{file_name}.docx")

    doc = Document()

    for path in user_images[user_id]:
        doc.add_picture(path, width=Inches(5.5))
        doc.add_paragraph("")

    doc.save(doc_path)

    with open(doc_path, "rb") as f:
        await query.message.reply_document(
            document=f,
            filename=f"{file_name}.docx",
            caption=texts[lang]["word_ready"]
        )

    await loading_msg.delete()


async def clear_files(query, user_id: int):
    lang = get_user_language(user_id)

    if user_id in user_images:
        user_images[user_id] = []

    if user_id in user_waiting_for_name:
        del user_waiting_for_name[user_id]

    if user_id in user_file_names:
        del user_file_names[user_id]

    cleanup_temp_folder(user_id)

    await query.message.reply_text(
        texts[lang]["cleared"],
        reply_markup=get_main_menu(lang)
    )


async def handle_filename_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    user_id = update.message.from_user.id
    lang = get_user_language(user_id)

    if user_id not in user_waiting_for_name:
        await update.message.reply_text(
            texts[lang]["send_photo"],
            reply_markup=get_main_menu(lang)
        )
        return

    raw_name = update.message.text
    clean_name = sanitize_filename(raw_name)

    if not clean_name:
        await update.message.reply_text(texts[lang]["name_empty"])
        return

    if len(clean_name) > 50:
        await update.message.reply_text(texts[lang]["name_too_long"])
        return

    action = user_waiting_for_name[user_id]
    user_file_names[user_id] = clean_name
    del user_waiting_for_name[user_id]

    if action == "pdf":
        await update.message.reply_text(texts[lang]["name_saved_pdf"])
        fake_query = type("obj", (), {"message": update.message})
        await make_pdf(fake_query, user_id, clean_name)

    elif action == "word":
        await update.message.reply_text(texts[lang]["name_saved_word"])
        fake_query = type("obj", (), {"message": update.message})
        await make_word(fake_query, user_id, clean_name)


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    action = query.data

    if action.startswith("lang_"):
        lang = action.split("_")[1]
        user_languages[user_id] = lang

        await query.message.reply_text(
            texts[lang]["welcome"],
            reply_markup=get_main_menu(lang)
        )
        return

    lang = get_user_language(user_id)

    if action == "make_pdf":
        if user_id not in user_images or len(user_images[user_id]) == 0:
            await query.message.reply_text(texts[lang]["no_images"])
            return

        user_waiting_for_name[user_id] = "pdf"
        await query.message.reply_text(texts[lang]["ask_name_pdf"])

    elif action == "make_word":
        if user_id not in user_images or len(user_images[user_id]) == 0:
            await query.message.reply_text(texts[lang]["no_images"])
            return

        user_waiting_for_name[user_id] = "word"
        await query.message.reply_text(texts[lang]["ask_name_word"])

    elif action == "clear_files":
        await clear_files(query, user_id)

    elif action == "help":
        await query.message.reply_text(
            texts[lang]["help"],
            reply_markup=get_main_menu(lang)
        )

    elif action == "change_lang":
        await query.message.reply_text(
            texts[lang]["choose_lang"],
            reply_markup=get_language_menu()
        )

    elif action == "choose_size":
        await query.message.reply_text(
            texts[lang]["choose_size"],
            reply_markup=get_size_menu(lang)
        )

    elif action.startswith("size_"):
        size_choice = action.split("_")[1]
        user_pdf_sizes[user_id] = size_choice

        await query.message.reply_text(
            texts[lang]["size_saved"],
            reply_markup=get_main_menu(lang)
        )

    elif action == "back_main":
        await query.message.reply_text(
            texts[lang]["send_photo"],
            reply_markup=get_main_menu(lang)
        )


def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_filename_input))

    print("Bot ishga tushdi...")
    app.run_polling()


if __name__ == "__main__":
    main()