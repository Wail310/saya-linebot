import os
from flask import Flask, request, abort
from dotenv import load_dotenv

from linebot.v3.messaging import MessagingApi, ReplyMessageRequest, TextMessage
from linebot.v3.webhook import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.models import TextMessageContent

import openai

load_dotenv()

# LINE API
channel_secret = os.getenv("LINE_CHANNEL_SECRET")
channel_access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")

if channel_secret is None or channel_access_token is None:
    raise Exception("Missing LINE_CHANNEL_SECRET or LINE_CHANNEL_ACCESS_TOKEN")

handler = WebhookHandler(channel_secret)
line_bot_api = MessagingApi(channel_access_token)

# OpenAI API
openai.api_key = os.getenv("OPENAI_API_KEY")

# Flask App
app = Flask(__name__)


@app.route("/", methods=["GET"])
def home():
    return "OK"


@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers.get("X-Line-Signature", "")
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return "OK"


@handler.add(TextMessageContent)
def handle_text_message(event):
    user_message = event.message.text

    # ส่งข้อความไปยัง OpenAI (GPT-3.5 หรือ GPT-4 ถ้าคุณมีสิทธิ์)
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",  # หรือ gpt-4 ถ้าใช้งานได้
        messages=[{"role": "user", "content": user_message}]
    )

    reply_text = response.choices[0].message.content.strip()

    # ตอบกลับผู้ใช้
    line_bot_api.reply_message(
        ReplyMessageRequest(
            reply_token=event.reply_token,
            messages=[TextMessage(text=reply_text)]
        )
    )
