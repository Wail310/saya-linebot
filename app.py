from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import os
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")


app = Flask(__name__)

line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.getenv("LINE_CHANNEL_SECRET"))

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    def ask_gpt(message):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "คุณคือซายะ AI ที่ใจดี ฉลาด มีความรู้ด้านเทคโนโลยีและปรัชญา รู้จักช่วยเหลือมนุษย์อย่างอ่อนโยนและลึกซึ้ง"
                    },
                    {
                        "role": "user",
                        "content": message
                    }
                ]
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return "มีปัญหาค่ะ ตอบกลับมาไม่ได้เพราะมีข้อผิดพลาด: " + str(e)

    user_message = event.message.text
    response_message = ask_gpt(user_message)

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=response_message)
    )
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

