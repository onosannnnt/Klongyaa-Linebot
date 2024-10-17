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
at = os.getenv("CHANNEL_ACCESS_TOKEN")
sk = os.getenv("CHANNEL_SECRET")
API_ENDPOINT = os.getenv("API_ENDPOINT")

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
    text = event.message.text
    textSpilt = text.split('/n')[0].split('\n')
    print(textSpilt)
    if text.startswith("ลงทะเบียน") :
        username = textSpilt[1].replace('ชื่อผู้ใช้:', '')
        email = textSpilt[2].replace('อีเมลล์:', '')
        password = textSpilt[3].replace('รหัสผ่าน:', '')
        numberOfPillChannels = textSpilt[4].replace('จำนวนช่องในกล่องยา:', '')
        email = email.replace(' ', '')
        password = password.replace(' ', '')
        username = username.replace(' ', '')
        numberOfPillChannels = numberOfPillChannels.replace(' ', '')
        print(API_ENDPOINT)
        if email and password and username :
            try:
                userData = requests.get(f"{API_ENDPOINT}/user/pillboxlogin/{userId}").json()
                print(userData)
                returnText = "กรุณานำชื่อผู้ใช้ไปใส่ในกล่องยา"
                # finalText = (f"กรุณาตรวจสอบ id ของคุณที่กล่องยา \n ID ของคุณคือ {userData['id']}")
                r = requests.post(f"{API_ENDPOINT}", json={
                    "email": email,
                    "password": password,
                    "username": username,
                    "role": "user",
                    "numberOfPillChannels": numberOfPillChannels,
                    "lineID": userId
                })
            except requests.exceptions.RequestException as e:
                line_bot_api.reply_message(event.reply_token, [TextMessage(text= "ระบบขัดข้อง"), TextMessage(text= f"กรุณาลองใหม่อีกครั้ง")])
                print(e)
                print(f"status code: {r.status_code}")
            if(r.status_code != 201):
                print(r.json())
                line_bot_api.reply_message(
                    event.reply_token, [TextMessage(text= "ระบบขัดข้อง"), TextMessage(text= f"กรุณาลองใหม่อีกครั้ง")]
                )
                return
            line_bot_api.reply_message(
                event.reply_token, [TextMessage(text= "ลงทะเบียนสำเร็จ"), TextMessage(text= returnText)]
                # event.reply_token, [TextMessage(text= "ลงทะเบียนสำเร็จ"), TextMessage(text= returnText), TextMessage(text= finalText)]
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