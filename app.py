from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

app = Flask(__name__)

import os
from dotenv import load_dotenv

load_dotenv()

at = os.getenv('CHANNEL_ACCESS_TOKEN')
sk = os.getenv('CHANNEL_SECRET')

line_bot_api = LineBotApi(at)
handler = WebhookHandler(sk)

@app.route('/')
def hello():
    return "Hello Flask-Heroku"


@app.route("/callback", methods=['POST'])
def callback():
    print('callback')
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    userId = str(event.source).split('"userId": "')[1].replace('"}', '')
    print("userId xxxx")
    print(userId)
    returnText = f"User id ของคุณ คือ {userId}"
    returnMessage = "ระบบได้รับ user id ของคุณเเล้ว เริ่มต้นการใช้งานสำเร็จ ✔️"
    if event.message.text == 'Uid' or event.message.text == 'uid':
        line_bot_api.reply_message(
            event.reply_token, [TextMessage(text= returnText), TextMessage(text= returnMessage)]
        )
        
            


if __name__ == "__main__":
    print('server startttt')
    app.run()