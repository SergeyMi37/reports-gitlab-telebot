#import datetime
from datetime import datetime, timedelta

from django.utils import timezone
from telegram import ParseMode, Update
from telegram.ext import CallbackContext

from tgbot.handlers.onboarding import static_text
from tgbot.handlers.utils.info import extract_user_data_from_update
from users.models import User
from tgbot.handlers.onboarding.keyboards import make_keyboard_for_start_command

from tgbot.handlers.admin.handlers import get_daily
from tgbot.system_commands import set_up_commands
from tgbot.main import bot
BR = chr(13)+chr(10)

def command_help(update: Update, context: CallbackContext) -> None:
    u, created = User.get_user_and_created(update, context)
    user_id = extract_user_data_from_update(update)['user_id']
    if created:
        text = static_text.start_created.format(first_name=u.first_name)
    else:
        text = static_text.start_not_created.format(first_name=u.first_name)
    text += BR+'/start: Табельные кнопки 🚀'
    text += BR+'/stats: Отчет за ЛРПО ежедневный по меткам "Табель" 📊'
    text += BR+'/daily_rating: Отчет ежедневный по меткам "Табель,Рейтинг" 📊'
    text += BR+'/daily_rating_noname: Отчет ежедневный по меткам "Табель,Рейтинг" обезличенный 📊'
    text += BR+'/weekly_rating: Отчет еженедельный по меткам "Табель,Рейтинг" 📊'
    text += BR+'/report type:daily is:rating date:2024-07-26 period:2024-07-22;2024-07-26  - Заказать отчет по ключевым параметрам 📨'
    #text += BR+'/broadcast: Отправить сообщение 📨'
    #text += BR+'/ask_location: Отправить локацию 📍'
    #text += BR+'/export_users: Экспорт users.csv 👥'
    text += BR+'/help: Перечень команд'
    context.bot.send_message(
        chat_id=u.user_id,
        text=text,
        parse_mode=ParseMode.HTML
    )
   

def command_start(update: Update, context: CallbackContext) -> None:
    u, created = User.get_user_and_created(update, context)

    if created:
        text = static_text.start_created.format(first_name=u.first_name)
    else:
        text = static_text.start_not_created.format(first_name=u.first_name)

    update.message.reply_text(text=text,
                              reply_markup=make_keyboard_for_start_command())

#
def secret_level_yesterday_rating(update: Update, context: CallbackContext) -> None:
    # callback_data: SECRET_LEVEL_BUTTON variable from manage_data.py
    """ Pressed 'secret_level_button_text' after /start command"""
    user_id = extract_user_data_from_update(update)['user_id']
    yesterday = datetime.now() + timedelta(days=-1)
    #print(yesterday)
    _day = str(yesterday.strftime("%Y-%m-%d"))
    text= get_daily(curday=_day,label="Рейтинг")
    context.bot.edit_message_text(
        text=text,
        chat_id=user_id,
        message_id=update.callback_query.message.message_id,
        parse_mode=ParseMode.HTML
    )

def secret_level(update: Update, context: CallbackContext) -> None:
    # callback_data: SECRET_LEVEL_BUTTON variable from manage_data.py
    """ Pressed 'secret_level_button_text' after /start command"""
    user_id = extract_user_data_from_update(update)['user_id']
    curday = str(datetime.today().strftime("%Y-%m-%d"))
    text= get_daily(curday=curday,label="Рейтинг")

    context.bot.edit_message_text(
        text=text,
        chat_id=user_id,
        message_id=update.callback_query.message.message_id,
        parse_mode=ParseMode.HTML
    )