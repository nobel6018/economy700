import os
import string
from dataclasses import dataclass
from datetime import datetime
from email.header import Header
from typing import List

import boto3
import pytz
import requests
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


def handler(event, context):
    article = get_today_article()

    subscriber_emails = get_subscriber_emails()
    send_email(subscriber_emails, article)

    send_slack_message(article)


@dataclass
class Article:
    id: int
    title: string
    content: string
    relatedKeywords: List[str]


def get_subscriber_emails() -> List[str]:
    dynamodb = boto3.resource('dynamodb')

    table = dynamodb.Table('email')
    response = table.scan()
    emails = response['Items']
    return list(map(lambda x: x['email'], emails))


def send_email(to_addrs: List[str], article: Article):
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText

    gmail_user = os.environ.get('GMAIL_USER')
    gmail_password = os.environ.get('GMAIL_PASSWORD')

    from_addr = gmail_user

    # MIME 메시지 생성
    msg = MIMEMultipart('alternative')
    msg['From'] = from_addr
    msg['To'] = Header("undisclosed-recipients:;")
    msg['Subject'] = f'오늘의 경제 단어: {article.title}'

    # HTML 이메일 본문 내용
    html = f"""\
    <html>
      <head></head>
      <body>
        <h3>❤️<a href="https://economy700.leedo.me/{article.id}.json">{article.id}. {article.title}</a>🍀</h3>
        <p style="padding: 12px; border-left: 4px solid #d0d0d0;">
          {article.content}
        </p>
        <p>연관검색어: {", ".join(article.relatedKeywords) if len(article.relatedKeywords) > 0 else "N/A"}</p>
      </body>
    </html>
    """

    # MIMEText 객체 생성 및 메시지에 추가
    part = MIMEText(html, 'html')
    msg.attach(part)

    # Gmail SMTP 서버 설정 및 이메일 전송
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)  # Gmail SMTP 서버 주소와 TLS 포트
        server.starttls()  # TLS 보안 시작
        server.login(gmail_user, gmail_password)

        server.sendmail(from_addr, to_addrs + [from_addr], msg.as_string())
        print(f"Email sent successfully to {to_addrs + [from_addr]}")
    except Exception as e:
        print(f"Failed to send email: {e}")
    finally:
        server.quit()


def send_slack_message(article: Article):
    client = WebClient(token=os.environ['SLACK_BOT_TOKEN'])

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


def get_today_article() -> Article:
    number = get_today_number()

    response = requests.get(f"https://economy700.leedo.me/{number}.json")
    json_data = response.json()
    article = Article(**json_data)

    return article
