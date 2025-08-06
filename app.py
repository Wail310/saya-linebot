import os
from flask import Flask, request, abort
from dotenv import load_dotenv

from linebot.v3.webhook import WebhookHandler
from linebot.v3.messaging import MessagingApi, Configuration, ApiClient, ReplyMessageRequest, TextMessage
from linebot.v3.webhooks import MessageEvent, TextMessageContent
from linebot.v3.exceptions import InvalidSignatureError

import openai

# Load environment variables
load_dotenv()

channel_secret = os.getenv("LINE_CHANNEL_SECRET")
channel_access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
openai.api_key = os.getenv("OPENAI_API_KEY")

if channel_secret is None or channel_access_token is None:
    raise Exception("Please set LINE_CHANNEL_SECRET and LINE_CHANNEL_ACCESS_TOKEN")

app = Flask(__name__)
handler = WebhookHandler(channel_secret)

configuration = Configuration(access_token=channel_access_token)
api_client = ApiClient(configuration)
line_bot_api = MessagingApi(api_client)


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


@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    user_message = event.message.text

    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",  # หรือ gpt-4 ถ้าเปิดใช้ได้
        messages=[{"role": "user", "content": user_message}]
    )

    reply_text = response.choices[0].message.content.strip()

    line_bot_api.reply_message(
        ReplyMessageRequest(
            reply_token=event.reply_token,
            messages=[TextMessage(text=reply_text)]
        )
    )
