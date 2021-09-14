
import json
import random

# Create your views here.
from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render

from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import *

from bot.models import *

line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
parser = WebhookParser(settings.LINE_CHANNEL_SECRET)


@csrf_exempt
def callback(request):
    if request.method == 'POST':
        signature = request.META['HTTP_X_LINE_SIGNATURE']
        body = request.body.decode('utf-8')
        try:
            events = parser.parse(body, signature)
        except InvalidSignatureError:
            return HttpResponseForbidden()
        except LineBotApiError:
            return HttpResponseBadRequest()

        for event in events:
            if isinstance(event, MessageEvent):
                get_message = event.message.text
                if '死者甦醒*' in get_message:
                    get_log(event)
                elif '遊戲開始' in get_message:
                    game_coda_start(event)
                elif '抽卡' in get_message or '發卡' in get_message:
                    wen_card(event,get_message)
                else:
                    save_log(event)
                    reply_message = nav(get_message,event)
                    if reply_message:
                        message=[]
                        message.append(TextSendMessage(text=reply_message))
                        line_bot_api.reply_message(event.reply_token,message)
        return HttpResponse()
    else:
        return HttpResponseBadRequest()

def game_coda_start(message):
    #取得群組基本資訊
    mes_type = message.source.type
    if 'group' in mes_type:
        mes_groupID = message.source.group_id
        obj_coda, created = coda.objects.get_or_create(groupID=mes_groupID,answer_num=random.randint(1, 7))
        line_bot_api.reply_message(message.reply_token, TextSendMessage(text='開'))
    line_bot_api.reply_message(message.reply_token, TextSendMessage(text='未開'))

def get_log(message):
    # 來找尋下一個id
    mes_id_list = []
    def find_prev_id(id, id_list):
        i = id_list.index(id)
        return id_list[i - 1]
    #獲取基本資料
    mes_text = message.message.text
    mes_userID = message.source.user_id
    mes_type = message.source.type

    #本次搜尋目標之前一封訊息
    q = mes_text.split('死者甦醒*')[1]
    this_messages = messagelog.objects.filter(message=q).order_by('-id').first()

    #取得所有相關訊息ID
    if 'group' in mes_type:
        mes_groupID = message.source.group_id
        all_messages = messagelog.objects.filter(groupID=mes_groupID).order_by('-id')
        for all_message in all_messages:
            mes_id_list.append(all_message.id)
    else:
        all_messages = messagelog.objects.filter(userID=mes_userID,groupID='').order_by('-id')
        for all_message in all_messages:
            mes_id_list.append(all_message.id)
    #取得隱藏訊息之ID
    hide_message_id = find_prev_id(this_messages.id, mes_id_list)
    hide_message = messagelog.objects.filter(id=hide_message_id).get()
    hide_message_text = hide_message.message
    hide_message_userID = hide_message.userID
    hide_message_userNAME = line_user.objects.filter(userID=hide_message_userID)
    if not hide_message_userNAME:
        line_user.objects.create(userID=hide_message_userID)
        contents = hide_message_text
    else:
        hide_message_userNAME = hide_message_userNAME.get().username
        if hide_message_userNAME:
            contents = '【' + hide_message_userNAME + '】：' + hide_message_text
        else:
            contents = hide_message_text
    line_bot_api.reply_message(message.reply_token,TextSendMessage(text= contents ))


def save_log(message):
    mes_text = message.message.text
    mes_type = message.source.type
    mes_userID = message.source.user_id
    if 'group' in mes_type:
        mes_groupID = message.source.group_id
        messagelog.objects.create(userID=mes_userID, groupID=mes_groupID, message=mes_text)
    else:
        messagelog.objects.create(userID=mes_userID, message=mes_text)



def nav(q,event):
    if '哈' in q or 'ㄏ' in q :
        return wen(q,event)
    elif '涼去' in q:
        return '搭去'
    else:
        return False

def wen(q,event):
    mes_userID = event.source.user_id
    mes_userNAME = line_user.objects.filter(userID=mes_userID)
    if mes_userNAME:
        mes_userNAME = mes_userNAME.get().username
    if '哈' in q:
        q_num = q.count('哈')
        if q_num == 1:
            word = '無言'
        elif q_num == 2:
            word = '老年人'
        elif q_num == 3:
            word = '敷衍'
        elif q_num == 4:
            word = '強迫整數'
        elif 4 < q_num and q_num <= 6:
            word = '朋友'
        elif 6 < q_num and q_num <= 8:
            word = '覺得你有趣'
        elif 8 < q_num and q_num <= 10:
            word = '喜歡你'
        elif 10 < q_num and q_num <= 12:
            word = '有求於你'
        elif 12 < q_num:
            word = '北七'
    elif 'ㄏㄚ' in q:
        word = 'ㄏㄚ三小'
    elif 'ㄏ' in q:
        if 'U1bcf57822f2e4b00567d003d07d63086' in mes_userID:
            word = '你沒救了拉'
        else:
            if mes_userNAME:
                word = mes_userNAME + '，你想學董育豪逆'
            else:
                word = '你別ㄏ了拉'
    else:
        return False
    return word

def wen_card(event,q):
    if '發卡' in q :
        if '集卡冊' in q:
            flex_message = FlexSendMessage(
                alt_text='小樂卡發動',
                contents={"type": "bubble", "body": {"type": "box", "layout": "vertical", "contents": [
                    {"type": "button", "style": "link", "height": "sm",
                     "action": {"type": "message", "label": "洗澡卡", "text": "發卡 洗澡"}},
                    {"type": "button", "style": "link", "height": "sm",
                     "action": {"type": "message", "label": "吹髮卡", "text": "發卡 吹頭髮"}},
                    {"type": "button", "style": "link", "height": "sm",
                     "action": {"type": "message", "label": "先忙卡", "text": "發卡 先忙"}},
                    {"type": "button", "style": "link", "height": "sm",
                     "action": {"type": "message", "label": "睡覺卡", "text": "發卡 睡覺"}},
                    {"type": "button", "style": "link", "height": "sm",
                     "action": {"type": "message", "label": "下次卡", "text": "發卡 下次"}},
                    {"type": "button", "style": "link", "height": "sm",
                     "action": {"type": "message", "label": "句點卡", "text": "發卡 句點"}},
                    {"type": "button", "style": "link", "height": "sm",
                     "action": {"type": "message", "label": "吃飯卡", "text": "發卡 吃飯"}},
                    {"type": "button", "style": "link", "height": "sm",
                     "action": {"type": "message", "label": "陷阱卡", "text": "發卡 陷阱卡"}},
                ]
                }}
            )
            line_bot_api.reply_message(event.reply_token, flex_message)
        else:
            if '洗澡' in q:
                title = '洗澡卡'
                text = '不好意思，我先去洗澡了'
                img_url = 'https://storage.googleapis.com/www-cw-com-tw/article/202003/article-5e82f4de60f19.jpg'
            elif '髮' in q:
                title = '吹頭髮卡'
                text = '我先去吹頭髮'
                img_url = 'https://cdn.bella.tw/files/S__27213871.jpg'
            elif '先忙' in q:
                title = '先忙卡'
                text = '我先忙喔，等等回'
                img_url = 'https://i.shangc.net/2017/0613/20170613040423380.jpg'
            elif '睡覺' in q:
                title = '睡覺卡'
                text = '我先睡囉'
                img_url = 'https://image.cache.storm.mg/styles/smg-800x533-fp/s3/media/image/2019/01/30/20190130-033419_U13613_M496272_cc3c.jpg?itok=hk8693pO'
            elif '下次' in q:
                title = '下次卡'
                text = '當你想果斷拒絕，但卻又想給希望'
                img_url = 'https://s3.ifanr.com/wp-content/uploads/2017/12/cal.jpg'
            elif '句點' in q:
                title = '句點卡'
                text = '。'
                img_url = 'https://i.imgur.com/bnlAlde.jpeg'
            elif '吃飯' in q:
                title = '吃飯卡'
                text = '先吃飯、先去買飯、先去煮飯等'
                img_url = 'https://i2.wp.com/dailycold.tw/wp-content/uploads/2020/01/54472-1-625x342-1.jpg?fit=625%2C342&ssl=1'
            elif '陷阱' in q:
                title = '陷阱卡'
                text = '吼哩拉(╯°Д°)╯︵┻━┻'
                img_url = 'https://wiki.komica.org/images/thumb/3/3b/%E8%81%96%E3%81%AA%E3%82%8B%E3%83%90%E3%83%AA%E3%82%A2-%E3%83%9F%E3%83%A9%E3%83%BC%E3%83%95%E3%82%A9%E3%83%BC%E3%82%B9-.jpg/250px-%E8%81%96%E3%81%AA%E3%82%8B%E3%83%90%E3%83%AA%E3%82%A2-%E3%83%9F%E3%83%A9%E3%83%BC%E3%83%95%E3%82%A9%E3%83%BC%E3%82%B9-.jpg'
            try:
                flex_message = FlexSendMessage(
                    alt_text='小樂卡發動',
                    contents={"type": "carousel", "contents": [{"type": "bubble", "body": {"type": "box", "layout": "vertical",
                                                                                           "contents": [
                                                                                               {"type": "image", "url": img_url,
                                                                                                "size": "full",
                                                                                                "aspectMode": "cover",
                                                                                                "aspectRatio": "2:3",
                                                                                                "gravity": "top"},
                                                                                               {"type": "box",
                                                                                                "layout": "vertical",
                                                                                                "contents": [{"type": "box",
                                                                                                              "layout": "vertical",
                                                                                                              "contents": [{
                                                                                                                               "type": "text",
                                                                                                                               "text": title,
                                                                                                                               "size": "xl",
                                                                                                                               "color": "#ffffff",
                                                                                                                               "weight": "bold"}]},
                                                                                                             {"type": "box",
                                                                                                              "layout": "baseline",
                                                                                                              "contents": [{
                                                                                                                               "type": "text",
                                                                                                                               "text": text,
                                                                                                                               "color": "#ebebeb",
                                                                                                                               "size": "sm",
                                                                                                                               "flex": 0}],
                                                                                                              "spacing": "lg"},
                                                                                                             {"type": "box",
                                                                                                              "layout": "vertical",
                                                                                                              "contents": [{
                                                                                                                               "type": "filler"},
                                                                                                                           {
                                                                                                                               "type": "box",
                                                                                                                               "layout": "baseline",
                                                                                                                               "contents": [
                                                                                                                                   {
                                                                                                                                       "type": "filler"},
                                                                                                                                   {
                                                                                                                                       "type": "text",
                                                                                                                                       "text": "重新抽卡",
                                                                                                                                       "color": "#ffffff",
                                                                                                                                       "flex": 0,
                                                                                                                                       "offsetTop": "-2px",
                                                                                                                                       "action": {
                                                                                                                                           "type": "message",
                                                                                                                                           "label": "action",
                                                                                                                                           "text": "抽卡"}},
                                                                                                                                   {
                                                                                                                                       "type": "filler"}],
                                                                                                                               "spacing": "sm"},
                                                                                                                           {
                                                                                                                               "type": "filler"}],
                                                                                                              "borderWidth": "1px",
                                                                                                              "cornerRadius": "4px",
                                                                                                              "spacing": "sm",
                                                                                                              "borderColor": "#ffffff",
                                                                                                              "margin": "xxl",
                                                                                                              "height": "40px"}],
                                                                                                "position": "absolute",
                                                                                                "offsetBottom": "0px",
                                                                                                "offsetStart": "0px",
                                                                                                "offsetEnd": "0px",
                                                                                                "backgroundColor": "#03303Acc",
                                                                                                "paddingAll": "20px",
                                                                                                "paddingTop": "18px"},
                                                                                               {"type": "box",
                                                                                                "layout": "vertical",
                                                                                                "contents": [{"type": "text",
                                                                                                              "text": "小樂牌",
                                                                                                              "color": "#ffffff",
                                                                                                              "align": "center",
                                                                                                              "size": "xs",
                                                                                                              "offsetTop": "3px"}],
                                                                                                "position": "absolute",
                                                                                                "cornerRadius": "20px",
                                                                                                "offsetTop": "18px",
                                                                                                "backgroundColor": "#ff334b",
                                                                                                "offsetStart": "18px",
                                                                                                "height": "25px",
                                                                                                "width": "53px"}],
                                                                                           "paddingAll": "0px"}}]}
                )
                line_bot_api.reply_message(event.reply_token, flex_message)
            except:
                wen_card(event, '發卡 集卡冊')
    elif '抽卡' in q:
        card_num = random.randint(1, 7)
        if card_num == 1:
            wen_card(event, '發卡 洗澡')
        elif card_num == 2:
            wen_card(event, '發卡 頭髮')
        elif card_num == 3:
            wen_card(event, '發卡 先忙')
        elif card_num == 4:
            wen_card(event, '發卡 睡覺')
        elif card_num == 5:
            wen_card(event, '發卡 下次')
        elif card_num == 6:
            wen_card(event, '發卡 句點')
        else:
            wen_card(event, '發卡 吃飯')



