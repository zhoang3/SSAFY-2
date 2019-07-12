# -*- coding: utf-8 -*-
import re
import urllib.request

from bs4 import BeautifulSoup

from flask import Flask
from slack import WebClient
from slackeventsapi import SlackEventAdapter
from slack.web.classes import extract_json
from slack.web.classes.blocks import *
from slack.web.classes.blocks import *
from slack.web.classes.elements import *
from slack.web.classes.interactions import MessageInteractiveEvent
import json

SLACK_TOKEN = "xoxb-678243449778-689220589060-fqIZp3qzvUGmT30y8OLvJPkw"
SLACK_SIGNING_SECRET = "f79f86a84fb949f70aaa1b1d1a56eaa0"

app = Flask(__name__)
# /listening 으로 슬랙 이벤트를 받습니다.
slack_events_adaptor = SlackEventAdapter(SLACK_SIGNING_SECRET, "/listening", app)
slack_web_client = WebClient(token=SLACK_TOKEN)

# 크롤링 함수 구현하기
def _crawl_set(text):
    if not "set" in text:
        return "`@<봇이름> type이름` 과 같이 멘션해주세요."

    # 여기에 함수를 구현해봅시다.
    url = 'https://docs.python.org/ko/3/library/stdtypes.html#set-types-set-frozenset'
    req = urllib.request.Request(url)

    source_code = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(source_code, "html.parser")

    funcNames = []
    text = []

    set = ['*<집합형 -- set, frozenset>*','\n']

    for i in (soup.find("div", id="set-types-set-frozenset").find_all("p")):
        if not i.get_text() in text:
            if len(text) >= 5:
                break
            text.append(i.get_text().strip().replace('¶',''))

    for i in (soup.find("div", id="set-types-set-frozenset").find_all("dt")):
        if not i.get_text() in funcNames:
            if len(funcNames) >= 2:
                break
            funcNames.append('*'+i.get_text().strip().replace('¶','')+'*')
    funcNames.append('\n')
    for i in (soup.find("div", id="set-types-set-frozenset").find_all("dl", class_="describe")):
        a = i.find("dt")
        b = i.find("dd")
        if not i.get_text() in funcNames:
            if len(funcNames) >= 5:
                break
            funcNames.append('*'+'#'+a.get_text().strip().replace('¶','').replace('*','')+'*')
            funcNames.append(b.get_text().strip().replace('¶', ''))

    for i in (soup.find("div", id="set-types-set-frozenset").find_all("dl", class_="method")):
        a = i.find_all("dt")
        b = i.find("dd")
        for aa in a:
            if not aa.get_text() in funcNames:
                # if len(funcNames) >= 10:
                #     break
                funcNames.append('*'+aa.get_text().strip().replace('¶','').replace('*','')+'*')
        funcNames.append(b.get_text().strip().replace('¶', '') + '\n')
    text.append('\n')
    message = set + text + funcNames

    return message

def _crawl_str(text):
    if not "str" in text:
        return "`@<봇이름> type이름` 과 같이 멘션해주세요."

    # 여기에 함수를 구현해봅시다.
    url = 'https://docs.python.org/ko/3/library/stdtypes.html'
    req = urllib.request.Request(url)

    source_code = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(source_code, "html.parser")

    funcNames = []
    text = []
    strClass = []

    txtStr = ['*<텍스트 시퀀스 -- str>*', '\n']

    for i in (soup.find("div", id="text-sequence-type-str").find_all("p")):
        if not i.get_text() in text:
            if len(text) >= 1:
                break
            text.append('“ ' + i.get_text().strip().replace('¶', '')+ '”')
    text.append('\n')

    for i in (soup.find("div", id="text-sequence-type-str").find_all("dt")):
        if not i.get_text() in strClass:
            if len(strClass) >= 2:
                break
            strClass.append('*'+i.get_text().strip().replace('¶', '')+'*')
    strClass.append('\n')

    strMethod = ['*--문자열 메서드--*']
    for i in (soup.find("div", id="string-methods").find_all("dl", class_="method")):
        a = i.find("dt")
        b = i.find("dd").find("p")
        if not a.get_text() in funcNames:
            # if len(funcNames) >= 10:
            #     break

            funcNames.append('*' + '- '+a.get_text().strip().replace('¶','').replace('*','')+'*')
            funcNames.append(b.get_text().strip().replace('¶', ''))

    message = txtStr + text + strClass + strMethod + funcNames

    return message

def _crawl_types(text):
    url = 'https://docs.python.org/ko/3/library/stdtypes.html'
    req = urllib.request.Request(url)

    source_code = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(source_code, "html.parser")

    message = []

    if text[13:] == 'set':
        message = _crawl_set(text)
    elif text[13:] == 'str':
        message = _crawl_str(text)
    elif text[13:] == 'dictionary':
        message = _crawl_dic(text)
    else:
        message = _crawl_sequence(text, soup)

    return u'\n'.join(message)

# 크롤링 함수 구현하기
def _crawl_sequence(text, soup):
    # 여기에 함수를 구현해봅시다.
    message = []
    # 공통 연산
    common_operations = []
    for row in soup.find("table", {"id" : "index-19"}).find_all("tr"):
        column = []
        try:
            column = row.find_all("td")
            common_operations.append(column[0].get_text() + " : " + column[1].get_text())
        except:
            pass

    if "list" in text:
        message = _crawl_list(text, soup)
    elif "tuple" in text:
        message = _crawl_tuple(text, soup)
    elif "range" in text:
        message = _crawl_range(text, soup)

    return message

def _crawl_list(text, soup):
    message = []

    title = ['*<시퀀스형 -- list>*', '\n']

    # list 정의
    list_decriptions = []
    for decription in soup.find("div", {"id" : "lists"}).find_all("p")[:9]:
        list_decriptions.append(decription.get_text())
    list_decriptions.append('\n')

    # 가변 연산
    mutable_operations = []
    for row in soup.find("table", {"id": "index-22"}).find_all("tr"):
        column = []
        try:
            column = row.find_all("td")
            mutable_operations.append('*'+column[0].get_text()+'*' + "\n" + column[1].get_text())
        except:
            pass

    message = title + list_decriptions + mutable_operations

    return message

def _crawl_tuple(text, soup):
    message = []
    title = ['*<시퀀스형 -- tuple>*', '\n']

    # tuple 정의
    tuple_decriptions = []
    tuple_decriptions.append(soup.find("div", {"id": "tuples"}).get_text().replace('¶',''))

    message = title + tuple_decriptions

    return message

def _crawl_range(text, soup):
    message = []
    title = ['*<시퀀스형 -- range>*', '\n']

    # range 정의
    range_decriptions = []
    range_decriptions.append(soup.find("div", {"id": "ranges"}).find("p").get_text())
    range_decriptions.append("\n")

    #range 예제
    example = []
    example.append(soup.find("div", {"id": "ranges"}).find("pre").get_text())

    message = title + range_decriptions + example

    return message

def _crawl_func(text):
    url = 'https://docs.python.org/ko/3/library/functions.html'
    req = urllib.request.Request(url)

    source_code = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(source_code, "html.parser")

    title = ['*<Built in Functions>*', '\n']
    functions = []
    function_decriptions = []
    message = []


    for function in soup.find_all("dl", {"class": "function"}):
        functions.append(function.find("dt").get_text().replace('¶', '').replace('*', ''))
        function_decriptions.append(function.find("p").get_text() + '\n')

    final = []
    for i in range(len(functions)):
        #print('!'+functions[i])
        final.append('*'+ '- ' + functions[i].strip().replace('*','')+'*')
        final.append(function_decriptions[i])

    message = title + final

    return u'\n'.join(message)

def _crawl_dic(text):
    if not "dictionary" in text:
        return "`@<봇이름> dic' 과 같이 멘션해주세요."
    url = 'https://docs.python.org/ko/3/library/stdtypes.html#mapping-types-dict'
    req = urllib.request.Request(url)
    source_code = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(source_code, "html.parser")

    dic = ['*< 매핑형 -- dictionary >*', '\n']
    summarys = []
    methods = []

    for summary in soup.find("div", {"id":"mapping-types-dict"}).find_all("p"):
        summarys.append('“ ' + summary.get_text() + '”' + '\n')

    for method in soup.find("div", {"id":"mapping-types-dict"}).find_all("dl", class_="method"):
        a = method.find("dt")
        b = method.find("dd").find("p")
        methods.append('*' + '- ' + a.get_text().strip().replace('¶', '').replace('*', '') + '*')
        methods.append(b.get_text().strip().replace('¶', '') + '\n')

    message = dic+summarys[:3]+['\n']+methods

    return message

# 챗봇이 멘션을 받았을 경우
@slack_events_adaptor.on("app_mention")
def app_mentioned(event_data):
    channel = event_data["event"]["channel"]
    text = event_data["event"]["text"]
    #print(event_data)
    block = ImageBlock(
        image_url= "https://t1.daumcdn.net/cfile/tistory/9921213B5AE5A32434",
        alt_text = "keymap_macOS"
    )
    block2 = ImageBlock(
        image_url="https://t1.daumcdn.net/cfile/tistory/99A6593B5AE5A32526",
        alt_text="keymap_Windows&Linux"
    )
    block3 = ImageBlock(
        image_url="http://namulms.com/m/subject/download/7",
        alt_text="snake"
    )
    block_help = SectionBlock(
        text=" ------------------------ 차자봇 ------------------------\n"
             "파이썬에 대한 모든걸 찾아주는 차자봇입니다.◟( ˘ ³˘)◞ ♡\n"
             '*' + "Built-in Type :  + '*' `@봇이름 타입이름`\n"
             "(예시: set, str, dictionary, list...)\n"
             '*' + "Built-in Function : + '*' `@봇이름 func`\n"
             '*' + "Pycharm 단축키: + '*' `@봇이름 keymap`\n"
             "사용법 다시 보려면 `@봇이름 help`"
    )

    bold_types = ['*' + '- list' + '*', '*' + '- tuple' + '*', '*' + '- range' + '*',  '*' +'- set' + '*', '*' + '- str' + '*', '*' + '- dictionary' + '*']
    types = ['list', 'tuple', 'range', 'set', 'str', 'dictionary']

    if text[13:] == 'type':
        slack_web_client.chat_postMessage(
            channel=channel,
            attachments=[{"pretext" : '*' + "### Type 리스트 ###" + '*', "text" : u'\n'.join(bold_types)}]
        )
    elif text[13:] == 'keymap':
        my_blocks = [block, block2]
        slack_web_client.chat_postMessage(
            channel=channel,
            blocks=extract_json(my_blocks)
        )
    elif text[13:] in types:
        message = _crawl_types(text)
        slack_web_client.chat_postMessage(
            channel=channel,
            attachments=[{"text": message}]
        )
    elif text[13:] == 'func':
        message = _crawl_func(text)
        slack_web_client.chat_postMessage(
            channel=channel,
            attachments=[{"pretext" : '*' + "### Function 리스트 ###" + '*', "text": message}]
        )
    elif text[13:] == 'help':
        my_blocks = [block3,block_help]
        slack_web_client.chat_postMessage(
            channel=channel,
            blocks=extract_json(my_blocks)
        )
    else:
        my_blocks = [block3,block_help]
        slack_web_client.chat_postMessage(
            channel=channel,
            blocks=extract_json(my_blocks)
        )

@app.route("/", methods=["GET"])
def index():
    return "<h1>Server is ready.</h1>"


if __name__ == '__main__':
    app.run('127.0.0.1', port=4040)








