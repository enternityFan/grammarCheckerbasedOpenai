#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@Project ：pythonLearning
@File ：grammarCheck.py
@Author ：HuntingGame
@Date ：2023-06-10 20:56
C'est la vie!!! enjoy ur day :D

hi,this is an app used for the english write praticer to correct the grammar and the拼写 error
in their sentence,i hope it can 对你有很大的帮助！





'''

import os
import string
import sys
from datetime import datetime

import markdown2
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextBrowser, QVBoxLayout
from PyQt5.QtCore import Qt, pyqtSignal, QThread
from pynput import keyboard
import pyautogui
import pygetwindow as gw
import openai
from redlines import Redlines
from IPython.display import display, Markdown, Latex, HTML, JSON
import Config
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='logs/app%s.log' % datetime.now().strftime("%Y%m%d%H%M%S"),
    filemode='w'
)
configReader = Config.ConfigReader("config/config.json")
# Create a logger
logger = logging.getLogger()



os.environ["http_proxy"] = "http://127.0.0.1:7890"
os.environ["https_proxy"] = "http://127.0.0.1:7890"
# 设置OpenAI API密钥
api_key = os.environ.get("OPENAI_API_KEY")

text = ""
prompt = f"First of all, if there is Chinese, please help me translate Chinese into proper English, and please explain the grammatical rules contained therein :```"


def get_completion(prompt, model="gpt-3.5-turbo", temperature=0):
    messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=temperature,
    )
    return response.choices[0].message["content"]

def config_openai(api_key):
    openai.api_key = api_key


def get_selected_text():
    try:

        # 从剪贴板获取选中文本
        selected_text = QApplication.clipboard()
        return selected_text.text()
    except:
        return ""
class HtmlTextViewer(QTextBrowser):
    def __init__(self):
        super().__init__()

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.parent().hide()
class TextPopupWindow(QMainWindow):
    def __init__(self, text):
        super().__init__()
        # 创建一个垂直布局管理器
        layout = QVBoxLayout()
        # 创建一个文本框用于显示 HTML 内容
        self.text_browser = HtmlTextViewer()
        self.text_browser.setOpenExternalLinks(True)  # 允许打开外部链接
        self.setCentralWidget(self.text_browser)
        self.setLayout(layout)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.CustomizeWindowHint)
        self.isSetText = False
        self.FontSize = configReader.get_value("FontSize")
    def setFontSize(self,htmlContent:string):
        # Define CSS styles
        htmlContent = """
        <!DOCTYPE html>
        <html>
        <head>
        <style>
        body {{
            font-size: {}px;
        }}
        </style>
        </head>
        <body>
        {}
        </body>
        </html>
        """.format(self.FontSize, htmlContent)
        return htmlContent

    def set_text(self, text):
        logging.debug("set_text is called!")
        self.isSetText= True
        print("process!...")

        # plz help me to address this sentence's grammar error,if it exists.i will very感激。
        response = get_completion(prompt + text + "```")
        diff = Redlines(text, response)
        formatted_output = markdown2.markdown(diff.output_markdown)
        formatted_output = self.setFontSize(formatted_output)
        self.text_browser.setHtml(formatted_output)
        self.isSetText = False

    def closeEvent(self, event):
        # 窗口关闭事件处理程序
        print("close event!")
        self.hide()
        event.ignore()

    def mouseDoubleClickEvent(self, event):
        # 窗口双击事件处理程序
        self.hide()
    def showEvent(self, event):
        # 获取当前鼠标位置
        cursor_pos = QCursor.pos()

        # 设置窗口位置为当前鼠标位置的下方
        self.move(cursor_pos.x(), cursor_pos.y() + 20)  # 在下方留出一定的空间

        # 调用父类的 showEvent
        super().showEvent(event)
class KeyboardListenerThread(QThread):
    text_selected = pyqtSignal(str)

    def __init__(self,window:TextPopupWindow):
        QThread.__init__(self)
        self.window = window


    def run(self):
#you are a very smart friend!
        def on_press(key):
            #print(key, "is press!")

            if str(key) == configReader.get_value("hot-key"):
                if self.window.isSetText:
                    print("正在发送请求。。。请稍后")
                    # TODO 可能有更好的解决方案，这里做的操作是，如果当前已经向openai发送了请求，那么就不再检测了
                    return True
                print(f"shift+1 被同时按下")
                selected_text = get_selected_text()
                print(selected_text)
                if selected_text:
                    self.text_selected.emit(selected_text)
            return True
        # 启动键盘监听器
        with keyboard.Listener(on_press=on_press) as listener:
            listener.join()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    config_openai(api_key)

    #
    print("start!")
    # 创建窗口对象并连接信号
    window = TextPopupWindow("")
    window.setWindowTitle("Text Popup Window")
    window.resize(800, 300)
    # 创建键盘监听线程
    keyboard_listener_thread = KeyboardListenerThread(window)
    keyboard_listener_thread.start()
    keyboard_listener_thread.text_selected.connect(window.set_text)
    keyboard_listener_thread.text_selected.connect(window.show)

    sys.exit(app.exec_())
