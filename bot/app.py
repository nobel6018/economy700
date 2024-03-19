import os
import string
from dataclasses import dataclass
from datetime import datetime
from typing import List

import pytz
import requests
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


def handler(event, context):
    send_slack_message()


def send_slack_message():
    client = WebClient(token=os.environ['SLACK_BOT_TOKEN'])

    article = get_today_article()

    try:
        response = client.chat_postMessage(
            channel="#general",
            text=f"<https://economy700.leedo.me/{article.id}.json|*❤️{article.id}. {article.title}🍀*>\n\n{article.content}\n\n연관검색어: {', '.join(article.relatedKeywords)}"
        )
        print("Message sent: ", response["message"]["text"])
    except SlackApiError as e:
        print(f"Error sending message: {e}")


# 오늘의 항목 번호 계산, 700일 주기로 반복
def get_today_number() -> int:
    seoul_timezone = pytz.timezone('Asia/Seoul')
    start_date = datetime(2024, 3, 10, tzinfo=seoul_timezone)
    current_date = datetime.now(seoul_timezone)

    days_diff = (current_date - start_date).days

    return (days_diff % 700) + 1


@dataclass
class Article:
    id: int
    title: string
    content: string
    relatedKeywords: List[str]


def get_today_article() -> Article:
    number = get_today_number()

    response = requests.get(f"https://economy700.leedo.me/{number}.json")
    json_data = response.json()
    article = Article(**json_data)

    return article
