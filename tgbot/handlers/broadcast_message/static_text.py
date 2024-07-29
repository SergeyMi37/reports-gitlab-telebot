reports_command = '/reports'
reports_no_access = "Извините, у вас нет доступа к этой функции."
reports_wrong_format = f'После ключевого слова {reports_command} через пробел нужно ввести параметры отчета.\n' \
                         f'Например\n' \
                         f'{reports_command} date:today labels:Табель,Рейтинг mode:noname ' \
                         f'date:yestoday - отчет за вчера\n' \
                         f'date:today - отчет за сегодня\n' \
                         f'mode:name - вклбяать в отчет ФИО и дату'
broadcast_command = '/broadcast'
broadcast_no_access = "Sorry, you don't have access to this function."
broadcast_wrong_format = f'To send message to all your users,' \
                         f' type {broadcast_command} command with text separated by space.\n' \
                         f'For example:\n' \
                         f'{broadcast_command} Hello, my users! This <b>bold text</b> is for you, ' \
                         f'as well as this <i>italic text.</i>\n\n' \
                         f'Examples of using <code>HTML</code> style you can found <a href="https://core.telegram.org/bots/api#html-style">here</a>.'
confirm_broadcast = "Confirm ✅"
decline_broadcast = "Decline ❌"
message_is_sent = "Message is sent ✅"
declined_message_broadcasting = "Message broadcasting is declined ❌"
error_with_html = "Can't parse your text in <code>HTML</code> style. Reason: \n{reason}"
