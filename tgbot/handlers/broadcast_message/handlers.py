import re

import telegram
from telegram import Update
from telegram.ext import CallbackContext

from dtb.settings import DEBUG
from .manage_data import CONFIRM_DECLINE_BROADCAST, CONFIRM_BROADCAST
from .keyboards import keyboard_confirm_decline_broadcasting
from .static_text import broadcast_command, broadcast_wrong_format, broadcast_no_access, error_with_html, \
    message_is_sent, declined_message_broadcasting,reports_command, reports_no_access, reports_wrong_format
from users.models import User
from users.tasks import broadcast_message
from datetime import datetime, timedelta
from tgbot.handlers.admin.reports_gitlab import put_report
import os
GITLAB_LABELS = os.getenv('GITLAB_LABELS')

def reports(update: Update, context: CallbackContext):
    """ Reports."""
    u = User.get_user(update, context)
    if not u.is_admin:
        update.message.reply_text(
            text=reports_no_access,
        )
    else:
        if update.message.text == reports_command:
            # user typed only command without text for the message.
            update.message.reply_text(
                text=reports_wrong_format,
                parse_mode=telegram.ParseMode.HTML,
            )
            return
        if " " in update.message.text:
            params = f"{update.message.text.replace(f'{reports_command} ', '')}"
        else:
            par = f"{update.message.text.replace(f'{reports_command}_', '')}"
            #fd=str(fromDate).replace("-","")
            #td=str(toDate).replace("-","")
            #lb=label.replace("Рейтинг","rating").replace("ВПР","vpr").replace("Табель","tabel")
        
        # Логика разбора параметров
        mode="name"
        labels=GITLAB_LABELS
        print('-------',params)
        if 'date:yesterday' in params:
            _fromDate = datetime.now() + timedelta(days=-1)
            fromDate=_fromDate.date()
            toDate=fromDate
        if 'date:today' in params:
            fromDate = datetime.today().date()
            toDate=fromDate
        if 'date:weekly' in params:
            _fromDate = datetime.now() + timedelta(days=-7)
            fromDate=_fromDate.date()
            toDate = datetime.today().date()
        if 'mode:noname' in params:
            mode="noname"
        if 'labels:' in params:
            labels = params.split('labels:')[1]
        if 'date:20' in params:
            _fromDate = f"{params} ".split('date:')[1].split(" ")[0].split(":")[0]
            fromDate = datetime.strptime(_fromDate, "%Y-%m-%d").date()
            _toDate = f"{params} ".split('date:')[1].split(" ")[0].split(":")[1]
            toDate = datetime.strptime(_toDate,  "%Y-%m-%d").date()
        
        #print('---Reports-params:',fromDate,toDate,labels,mode)
        put_report(update=update, fromDate=fromDate,toDate=toDate,label=labels,mode=mode)

def broadcast_command_with_message(update: Update, context: CallbackContext):
    """ Type /broadcast <some_text>. Then check your message in HTML format and broadcast to users."""
    u = User.get_user(update, context)

    if not u.is_superadmin:
        update.message.reply_text(
            text=broadcast_no_access,
        )
    else:
        if update.message.text == broadcast_command:
            # user typed only command without text for the message.
            update.message.reply_text(
                text=broadcast_wrong_format,
                parse_mode=telegram.ParseMode.HTML,
            )
            return

        text = f"{update.message.text.replace(f'{broadcast_command} ', '')}"
        markup = keyboard_confirm_decline_broadcasting()

        try:
            update.message.reply_text(
                text=text,
                parse_mode=telegram.ParseMode.HTML,
                reply_markup=markup,
            )
        except telegram.error.BadRequest as e:
            update.message.reply_text(
                text=error_with_html.format(reason=e),
                parse_mode=telegram.ParseMode.HTML,
            )


def broadcast_decision_handler(update: Update, context: CallbackContext) -> None:
    # callback_data: CONFIRM_DECLINE_BROADCAST variable from manage_data.py
    """ Entered /broadcast <some_text>.
        Shows text in HTML style with two buttons:
        Confirm and Decline
    """
    broadcast_decision = update.callback_query.data[len(CONFIRM_DECLINE_BROADCAST):]

    entities_for_celery = update.callback_query.message.to_dict().get('entities')
    entities, text = update.callback_query.message.entities, update.callback_query.message.text

    if broadcast_decision == CONFIRM_BROADCAST:
        admin_text = message_is_sent
        user_ids = list(User.objects.all().values_list('user_id', flat=True))

        if DEBUG:
            broadcast_message(
                user_ids=user_ids,
                text=text,
                entities=entities_for_celery,
            )
        else:
            # send in async mode via celery
            broadcast_message.delay(
                user_ids=user_ids,
                text=text,
                entities=entities_for_celery,
            )
    else:
        context.bot.send_message(
            chat_id=update.callback_query.message.chat_id,
            text=declined_message_broadcasting,
        )
        admin_text = text

    context.bot.edit_message_text(
        text=admin_text,
        chat_id=update.callback_query.message.chat_id,
        message_id=update.callback_query.message.message_id,
        entities=None if broadcast_decision == CONFIRM_BROADCAST else entities,
    )
