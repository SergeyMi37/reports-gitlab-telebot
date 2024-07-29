#from datetime import timedelta

from django.utils.timezone import now
from telegram import ParseMode, Update
from telegram.ext import CallbackContext

from tgbot.handlers.admin import static_text
from tgbot.handlers.admin.utils import _get_csv_from_qs_values
from tgbot.handlers.utils.decorators import admin_only, send_typing_action
from users.models import User

import os
from typing import Any
#import datetime
from datetime import datetime, timedelta
import pytz
import requests
import json
from tgbot.handlers.admin import static_text

CERT_FILE = os.getenv('CERT_FILE')
CERT_KEY_FILE = os.getenv('CERT_KEY_FILE')
ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
GRAPHQL_URL = os.getenv('GRAPHQL_URL')
GITLAB_URL = os.getenv('GITLAB_URL')
GITLAB_LABELS = os.getenv('GITLAB_LABELS')

def command_daily(update: Update, context: CallbackContext) -> None:
    u = User.get_user(update, context)
    if not u.is_admin:
        update.message.reply_text(static_text.only_for_admins)
        return
    update.message.reply_text(
        text=get_report(fromDate=datetime.today().date(),label="Табель",mode="name"),
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )

def command_daily_rating_noname(update: Update, context: CallbackContext) -> None:
    u = User.get_user(update, context)
    if not u.is_admin:
        update.message.reply_text(static_text.only_for_admins)
        return
    update.message.reply_text(
        text=get_report(fromDate=datetime.today().date(),label="Табель,Рейтинг",mode="noname"),
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )

def command_daily_rating(update: Update, context: CallbackContext) -> None:
    u = User.get_user(update, context)
    if not u.is_admin:
        update.message.reply_text(static_text.only_for_admins)
        return
    update.message.reply_text(
        text=get_report(fromDate=datetime.today().date(),label="Табель,Рейтинг",mode="name"),
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )

def command_weekly_rating(update: Update, context: CallbackContext) -> None:
    u = User.get_user(update, context)
    
    _fromDate = datetime.now() + timedelta(days=-7)
    fromDate=_fromDate.date()
    toDate = datetime.today().date()
    if not u.is_admin:
        update.message.reply_text(static_text.only_for_admins)
        return
    text=get_report(fromDate=fromDate,toDate=toDate,label="Табель,Рейтинг",mode="name")
    print('--',text)
    ot=0 #!!!!!!!!!!
    po=4000
    do=po
    
    update.message.reply_text(
        text=text,
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )

def tz_to_moscow(date_time: str) -> datetime:
    dt = datetime.strptime(date_time, '%Y-%m-%dT%H:%M:%SZ')
    moscow_tz = pytz.timezone('Europe/Moscow')
    dt_utc = dt.replace(tzinfo=pytz.UTC)
    dt_moscow = dt_utc.astimezone(moscow_tz)
    #output_string = dt_moscow.strftime('%Y-%m-%d %H:%M:%S %Z%z')
    return dt_moscow.date()

def get_issues(url: str,
                    labels: str = 'Табель',
                    scope: str = 'all',
                    state: str = 'opened',
                    due_date: str = 'month') -> tuple[int, Any]:
  ret=""
  errno = "code.CODE_GITLAB_GET_ISSUE_OK"
  _url='{0:s}?labels={1:s}&scope={2:s}&state={3:s}&due_date={4:s}&per_page=100'.format(GITLAB_URL, labels, scope, state, due_date)
  try:
    headers = {
        #'Authorization': 'Bearer {0:s}'.format(ACCESS_TOKEN),
        'PRIVATE-TOKEN': ACCESS_TOKEN,
        'Accept': 'application/json;odata=verbose'
        }
    #print('---',_url,headers)
    responce = requests.get(_url,verify=False,headers=headers)
    response_list=responce.json()
    for it in response_list:
        print(it["iid"],it["title"],it['updated_at'])
        ret=ret +f"/n{it['iid']} {it['title']} {it['updated_at']}"

  except Exception as e:
    errno = "code.CODE_GITLAB_GET_ISSUE_FAIL"
    ret=e.args.__repr__()
    answer = {
      "errno": errno,
      'err_message': '{0}:{1}'.format("code.get_message(errno)", e.args.__repr__())
    }
  return errno, ret

def get_open_issues(url: str,
                    labels: str = 'Табель',
                    scope: str = 'all',
                    state: str = 'opened',
                    due_date: str = 'month') -> tuple[int, Any]:
  ret=""
  errno = "code.CODE_GITLAB_GET_ISSUE_OK"
  _url='{0:s}?labels={1:s}&scope={2:s}&state={3:s}&due_date={4:s}&per_page=100'.format(GITLAB_URL, labels, scope, state, due_date)
  headers = {
        #'Authorization': 'Bearer {0:s}'.format(ACCESS_TOKEN),
        'PRIVATE-TOKEN': ACCESS_TOKEN,
        'Accept': 'application/json;odata=verbose'
        }
  print('---',_url,headers)
  try:
      response = requests.get(_url,verify=False,headers=headers)
      if response.status_code == 200:
        answer = json.loads(response.text)
        return "code.CODE_GITLAB_GET_ISSUE_OK", answer
      elif response.status_code == 404:
        return "code.CODE_GITLAB_ISSUE_EMPTY", None
      else:
        errno = "code.CODE_GITLAB_GET_ISSUE_FAIL"
        answer = {
          "errno": errno,
          'err_message': '{0:s}:{1:s}'.format(errno, response.text)
        }
        raise Exception(answer.get('err_message'))
  except Exception as e:
    errno = "code.CODE_GITLAB_GET_ISSUE_FAIL"
    answer = {
      "errno": errno,
      'err_message': '{0}:{1}'.format(errno, e.args.__repr__())
    }
    return errno, answer

def post_issue(url: str = GRAPHQL_URL, number_issue: int = None) -> tuple[int, Any]:
  headers = {
    'Authorization': 'Bearer {0:s}'.format(ACCESS_TOKEN),
    'Content-Type': 'application/json'
  }
  bodies = {
    "operationName": "issueTimeTrackingReport",
    "variables": {
      "id": "gid://gitlab/Issue/{0}".format(number_issue)
    },
    "query": "query issueTimeTrackingReport($id: IssueID\u0021) {\n  issuable: issue(id: $id) {\n    id\n    title\n    timelogs (first: 100) {\n      nodes {\n        ...TimelogFragment\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment TimelogFragment on Timelog {\n  __typename\n  id\n  timeSpent\n  user {\n    id\n    name\n    __typename\n  }\n  spentAt\n  note {\n    id\n    body\n    __typename\n  }\n  summary\n  userPermissions {\n    adminTimelog\n    __typename\n  }\n}"
  }
  try:
      response = requests.post(url=url, verify=False, headers=headers, json=bodies)
      if response.status_code == 200:
        answer = json.loads(response.text)
        return "code.CODE_GITLAB_GET_ISSUE_TRACKING_OK", answer
      elif response.status_code == 404:
        return "code.CODE_GITLAB_ISSUE_TRACKING_EMPTY", None
      else:
        errno = "code.CODE_GITLAB_GET_ISSUE_TRACKING_FAIL"
        answer = {
          "errno": errno,
          'err_message': errno
        }
        raise Exception(answer.get('err_message'))
  except Exception as e:
    errno = "code.CODE_GITLAB_GET_ISSUE_TRACKING_FAIL"
    answer = {
      "errno": errno,
      'err_message': '{0}:{1}'.format(errno, e.args.__repr__())
    }
    return errno, answer

def get_issues_id(url: str = GITLAB_URL, labels: str = GITLAB_LABELS, scope: str = 'all', ) -> tuple[int, Any]:
  '''
  Функция REST API Gitlab для получения открытых issue
  :param url: url gitlab ресурса
  :param labels: Метки которые позволяют найти нужный контекст
  :param scope: область issue по умолчанию берутся все, а не текущего пользователя
  :return: list[id]
  '''
  errno, answer = get_open_issues(url=url, labels=labels, scope=scope)
  if errno == "code.CODE_GITLAB_GET_ISSUE_OK":
    issues_id = []
    for issue in answer:
      issues_id.append(int(issue.get('id')))
      print("=",issue.get('id'),issue.get('title'))
    return errno, issues_id
  else:
    return errno, answer

def get_report_issue(id_issue: int = None, fromDate: datetime="", toDate: datetime="", mode: str='name') -> tuple[int, Any, str]:
  '''
  Получение отчета прикрепленного к конкретному issue
  :param id_issue: id обсуждения
  :return: список содержащий информацию для отчета по обсуждению
  '''
  errno, answer = post_issue(number_issue=id_issue)
  #if id_issue==721:print("===",id_issue,answer)
  if errno == "code.CODE_GITLAB_GET_ISSUE_TRACKING_OK":
    if answer.get('data') is not None:
      if answer.get('data').get('issuable') is not None:
        answer_list = []
        summ=""
        answer_item = dict()
        #answer_item['id_issue'] = validate_int_is_none(get_last_for_split(answer.get('data').get('issuable').get('id')))
        answer_item['title'] = answer.get('data').get('issuable').get('title')
        for item in answer.get('data').get('issuable').get('timelogs').get('nodes'):
          answer_item['name'] = item.get('user').get('name')
          answer_item['summary'] = str(item.get('summary'))
          answer_item['note'] = item.get('note')
          _spentAt=item.get('spentAt')
          if 'T20:00:00Z' in _spentAt:
             _spentAt = _spentAt.replace('T20:00:00Z','T21:00:00Z') #!!!!!
          answer_item['spent_at'] = tz_to_moscow(_spentAt)
          #if id_issue==721:            print("---",answer_item['name'],answer_item['spent_at'],str(item.get('summary')))
          if answer_item['spent_at']>=fromDate and (answer_item['spent_at']<=toDate):
            #if id_issue==721:              print("------",answer_item['spent_at'],str(item.get('summary')))
            userfio=''
            if mode=="name":
                userfio=f'{answer_item["name"]} {answer_item["spent_at"].strftime("%Y-%m-%d")}{static_text.BR}'
            summ += f"{userfio} {item.get('summary')}{static_text.BR+static_text.BR}"
          answer_list.append(answer_item)
        return errno, answer_list, summ
      else:
        errno = "code.CODE_GITLAB_ISSUE_TRACKING_EMPTY"
        answer = {
          "errno": errno,
          'err_message': (errno)
        }
    else:
      errno = "code.CODE_GITLAB_BAD_REQUEST"
      err_message = answer.get('errors')[0].get('message')
      answer = {
        'errno': errno,
        'err_message': f'{(errno)}:{err_message}'
      }
    return errno, answer
  else:
    return errno, answer

def admin_old(update: Update, context: CallbackContext) -> None:
    """ Show help info about all secret admins commands """
    u = User.get_user(update, context)
    if not u.is_admin:
        update.message.reply_text(static_text.only_for_admins)
        return
    update.message.reply_text(static_text.secret_admin_commands)

def get_report(label: str = "Табель", fromDate: datetime="", toDate: datetime="", mode: str='name'):
    
    if toDate=='':
       toDate=fromDate
    if toDate==fromDate:
      _date=f'за {fromDate}'
    else:
      _date=f'с {fromDate} по {toDate}'
    errno, answer = get_issues_id(GITLAB_URL,label)
    #print('---',errno, answer)
    summ=f"{label}{static_text.BR}<b>Выполненные мероприятия {_date}</b>{static_text.BR+static_text.BR}"
    sum=summ
    if errno == "code.CODE_GITLAB_GET_ISSUE_OK":
        for item in answer:
            errno, answer, _summ = get_report_issue(id_issue=item, fromDate=fromDate, toDate=toDate, mode=mode)
            summ=summ+_summ
        if summ==sum:
           summ=summ+' не найдено'
        summ += static_text.BR+'/help'
        return summ[:4090]
    else:
       return errno


