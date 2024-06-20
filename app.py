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

# importing the requests library
import requests

app = Flask(__name__)

import os
from dotenv import load_dotenv

load_dotenv()
at = os.getenv("ACCESS_TOKEN")
sk = os.getenv("SECRET_KEY")

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
    print(event)
    userId = str(event.source).split('"userId": "')[1].replace('"}', '')
    returnText = f"User id ของคุณ คือ {userId}"
    returnMessage = "ระบบได้รับ user id ของคุณเเล้ว เริ่มต้นการใช้งานสำเร็จ ✔️"
    finalMessage = "กรุณานำ User ID ไปใส่ช่อง userID ในกล่องยา"
    text = event.message.text
    textSpilt = text.split('/n')[0].split('\n')
    if text.startswith("ลงทะเบียน") :
        email = textSpilt[1].replace('email: ', '')
        password = textSpilt[2].replace('password: ', '')
        username = textSpilt[3].replace('username: ', '')
        print(email)
        print(password)
        print(username)
        print(userId)
        if email and password and username :
            print(email)
            print(password)
            print(username)
            API_ENDPOINT = os.environ.get("API_ENDPOINT")
            try:
                r = requests.post(API_ENDPOINT, json={
                    "email": email,
                    "password": password,
                    "username": username,
                    "confirmPassword": password,
                    "lineUID": userId
                })
            except requests.exceptions.RequestException as e:
                line_bot_api.reply_message(event.reply_token, [TextMessage(text= "ลงทะเบียนไม่สำเร็จ เนื่องจากข้อมูลไม่ถูกต้อง"), TextMessage(text= f"กรุณาลองใหม่อีกครั้ง")])

            print(r.json())

            line_bot_api.reply_message(
                event.reply_token, [TextMessage(text= "ลงทะเบียนสำเร็จ"), TextMessage(text= returnMessage), TextMessage(text= returnText), TextMessage(text= finalMessage)]
                # event.reply_token, [TextMessage(text= "ลงทะเบียนสำเร็จ"), TextMessage(text= f"User id ของคุณ คือ {userId}")]
            )
        else:
            line_bot_api.reply_message(
                event.reply_token, [TextMessage(text= "ลงทะเบียนไม่สำเร็จ"), TextMessage(text= f"เนื่องจากข้อมูลไม่ครบถ้วน")]
            )
    # if event.message.text == 'Uid' or event.message.text == 'uid':
    #     line_bot_api.reply_message(
    #         event.reply_token, [TextMessage(text= returnText), TextMessage(text= returnMessage)]
    #     )
        
            


if __name__ == "__main__":
    print('server startttt')
    app.run()