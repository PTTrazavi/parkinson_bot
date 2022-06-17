from django.conf import settings
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseForbidden, HttpResponse
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from linebot import (LineBotApi, WebhookHandler)
from linebot.exceptions import (InvalidSignatureError)
from linebot.models import (
    MessageEvent,
    TextMessage,
    TextSendMessage,
    ImageMessage,
    ImageSendMessage,
)
import os
import time, datetime
from uuid import uuid1
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
import requests
from .util import imgtool, p_detection
from django.views.generic import ListView
from .models import Imageupload

YOUR_CHANNEL_ACCESS_TOKEN = settings.LINE_CHANNEL_ACCESS_TOKEN
YOUR_CHANNEL_SECRET = settings.LINE_CHANNEL_SECRET

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)

@csrf_exempt
def callback(request):
    signature = request.META["HTTP_X_LINE_SIGNATURE"]
    body = request.body.decode('utf-8')
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        HttpResponseForbidden()
    return HttpResponse('OK', status=200)

# オウム返し
@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text="請傳一張圖"))

@handler.add(MessageEvent, message=ImageMessage)
def handle_image_message(event):
    #save user provided image in the folder
    with open("media/images/temp.jpg", 'wb') as fd:
    # with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../media/images/temp.jpg'), 'wb') as fd: # GCS
        for chunk in line_bot_api.get_message_content(event.message.id).iter_content():
            fd.write(chunk)

    img_temp = Image.open("media/images/temp.jpg")
    # img_temp = Image.open(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../media/images/temp.jpg')) #GCS

    #save in Django DB
    temp_name = str(uuid1())
    temp_name_ext = temp_name + ".jpg"
    img_io = BytesIO()
    img_temp.save(img_io, format='JPEG')
    img_content = ContentFile(img_io.getvalue(), temp_name_ext)
    date_of_upload = str(datetime.datetime.today())
    img = Imageupload(image_file=img_content, title=temp_name, date_of_upload = date_of_upload)
    img.save()

    #process the image to make some changes
    # img_out, img_pre = imgtool("media/images/" + temp_name + ".jpg", True)
    if 'http' in img.image_file.url:
        img_out, img_pre, class_name = p_detection(img.image_file.url[:]) # GCS
        #send back the message id (used for debug)
        # image_message1 = TextSendMessage(text=str(line_bot_api.get_message_content(event.message.id)) + "AI處理圖片中請稍等10~15秒")
        #send back the original image sent by the user
        image_message2 = [
                TextSendMessage(
                text = "小帕AI預測："+class_name
                                    ),
                ImageSendMessage(
                                        original_content_url=img_out,
                                        preview_image_url   =img_out
                                    )]
    else:
        img_out, img_pre, class_name = p_detection(img.image_file.url[1:]) # local
        #send back the message id (used for debug)
        # image_message1 = TextSendMessage(text=str(line_bot_api.get_message_content(event.message.id)) + "AI處理圖片中請稍等10~15秒")
        #send back the original image sent by the user
        image_message2 = [
                TextSendMessage(
                text = "小帕AI預測："+class_name
                                    ),
                ImageSendMessage(
                                        original_content_url='https://3fd2d44ddddb.ngrok.io' + img_out,
                                        preview_image_url   ='https://3fd2d44ddddb.ngrok.io' + img_out
                                    )]

    #line_bot_api.reply_message(event.reply_token, image_message1)
    line_bot_api.reply_message(event.reply_token, image_message2)
