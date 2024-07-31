from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from tgbot.handlers.onboarding.manage_data import SECRET_LEVEL_BUTTON
from tgbot.handlers.onboarding.static_text import github_button_text, secret_level_button_text


def make_keyboard_for_start_command() -> InlineKeyboardMarkup:
    buttons = [[
        #InlineKeyboardButton(github_button_text, url="https://github.com/ohld/django-telegram-bot"),
        InlineKeyboardButton("ЛРПО", url="https://git.lab.nexus/ctz/lab/tabel/-/issues/?sort=updated_desc&state=opened&first_page_size=100"),
        InlineKeyboardButton("Рейтинг", url="https://git.lab.nexus/ctz/lab/tabel/-/issues/?sort=updated_desc&state=opened&label_name%5B%5D=%D0%A0%D0%B5%D0%B9%D1%82%D0%B8%D0%BD%D0%B3&first_page_size=20"),
        InlineKeyboardButton("Наука", url="https://git.lab.nexus/ctz/lab/tabel/-/issues/?sort=updated_desc&state=opened&label_name%5B%5D=%D0%9D%D0%B0%D1%83%D0%BA%D0%B0&first_page_size=20"),
        InlineKeyboardButton("ВПР", url="https://git.lab.nexus/ctz/lab/tabel/-/issues/?sort=updated_desc&state=opened&first_page_size=100"),
        InlineKeyboardButton("ЦУВР", url="https://git.lab.nexus/ctz/lab/tabel/-/issues/?sort=updated_desc&state=opened&first_page_size=100"),
        InlineKeyboardButton("Рубеж", url="https://git.lab.nexus/ctz/lab/tabel/-/issues/?sort=updated_desc&state=opened&first_page_size=100"),
        #InlineKeyboardButton(secret_level_button_text, callback_data=f'{SECRET_LEVEL_BUTTON}')
    ]]

    return InlineKeyboardMarkup(buttons)
