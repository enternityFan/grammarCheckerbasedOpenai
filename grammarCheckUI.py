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
import ctypes
import json
import os
import re
import string
import sys
import time
from asyncio import sleep
from datetime import datetime

from pykeyboard import PyKeyboard
import clipboard
import markdown2
from PyQt5.QtGui import QCursor, QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextBrowser, QVBoxLayout, QMessageBox, QWidget, QSystemTrayIcon, \
    QAction, QMenu, QSizePolicy, QSpacerItem
from PyQt5.QtCore import Qt, pyqtSignal, QThread, QPoint, QRect, QEvent, QCoreApplication
from pynput import keyboard
import pyautogui
import pygetwindow as gw
import openai
from pynput.keyboard import Key
from redlines import Redlines
from IPython.display import display, Markdown, Latex, HTML, JSON
import Config
import logging
import keyboard as kb
# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='logs/app%s.log' % datetime.now().strftime("%Y%m%d%H%M%S"),
    filemode='w'
)
configReader = Config.ConfigReader("config/config.json", "EWA")
# Create a logger
logger = logging.getLogger()
# 创建控制台处理器
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
# 将处理器添加到日志记录器
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)


os.environ["http_proxy"] = "http://127.0.0.1:7890"
os.environ["https_proxy"] = "http://127.0.0.1:7890"
# 设置OpenAI API密钥
if configReader.get_value("openai_api_key") != "":
    api_key = configReader.get_value("openai_api_key")
else:
    api_key = os.environ.get("OPENAI_API_KEY")





def config_openai(api_key):
    openai.api_key = api_key


def get_selected_text():
    try:

        # 打印剪贴板内容
        # 延迟一段时间，等待剪贴板内容的更新
        time.sleep(0.5)
        selected_text = clipboard.paste()
        return selected_text
    except:
        return ""


class MyGeneratorJosnError(Exception):
    pass
class HtmlTextViewer(QTextBrowser):
    def __init__(self):
        super().__init__()

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.parent().parent().hide()



class TextPopupWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # 创建一个垂直布局管理器
        layout = QVBoxLayout()

        self.setWindowIcon(QIcon("resource/icon.png"))
        self.text_browser = HtmlTextViewer()
        self.text_browser.setOpenExternalLinks(True)  # 允许打开外部链接
        #self.text_browser.setContentsMargins(0, 0, 120, 120)# 设置控件边界
        layout.addWidget(self.text_browser)
        # 设置主窗口的布局
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)


        self.setWindowFlags(Qt.WindowStaysOnTopHint )
        self.isSetText = False
        self.pre_selected_text = ""

        self.drag_position = QPoint()
        self.setMouseTracking(True)  # 开启鼠标追踪
        self.resize_handle_size = 10  # 设置边缘调整大小的触发区域大小
        # ================处理线程相关的
        self.processFlag = False
        # =================设置系统托管相关=================
        # 创建系统托盘图标
        self.tray_icon = QSystemTrayIcon(QIcon("resource/icon.png"), self)
        self.tray_icon.setToolTip("chatGPT Writer Assitant")
        # 创建菜单
        self.tray_menu = QMenu(self)
        self.action_config = QAction("配置文件", self)
        self.action_quit = QAction("退出", self)
        self.action_quit.triggered.connect(QApplication.quit)
        self.action_config.triggered.connect(self.handle_action_config)

        self.tray_menu.addAction(self.action_config)
        self.tray_menu.addAction(self.action_quit)

        # 设置系统托盘图标的菜单
        self.tray_icon.setContextMenu(self.tray_menu)

        # 将系统托盘图标的 activated 信号连接到槽函数
        self.tray_icon.activated.connect(self.handle_tray_activated)

        self.FontSize = None
        self.hot_key = None
        self.max_token = None
        self.prompt = ""
        self.setConfig()
        self.tray_icon.show()
    def setConfig(self):
        self.FontSize = configReader.get_value("FontSize")
        self.hot_key = configReader.get_value("hot-key")
        self.max_token = configReader.get_value("max_token")
        self.prompt = configReader.get_value("prompt")
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

    def json_to_html(self,data,originalText):
        html = '<html>\n<head>\n<style>\n' \
               'body {{font-size: {}px; font-family: Arial, sans-serif; }}\n' \
               'span.key {{ color: #008000; font-weight: bold; }}\n' \
               'span.value {{ color: #000000; }}\n' \
               'span.correct-sentence {{ color: #FF0000; font-weight: bold; }}\n' \
               '</style>\n</head>\n<body>\n'.format(self.FontSize)

        diff = Redlines(originalText, data["correct_sentence"])
        html_correct_sentence = markdown2.markdown(diff.output_markdown)
        html +=html_correct_sentence
        if 'evaluate' in data:
            evaluate = data['evaluate']
            html += '<p><span class="key">evaluate: </span><span class="value">{}</span></p>\n'.format(evaluate)
        for filed in data:
            if filed in ("evaluate","correct_sentence"):
                continue
            filed = data[filed]
            html += '<p><span class="key">explain:</span></p>\n<ul>\n'
            for key, value in filed.items():
                html += '<li><span class="key">{}</span>: <span class="value">{}</span></li>\n'.format(key, value)
            html += '</ul>\n'
        html += '</body>\n</html>'
        return html
    def process_text(self,text):

        json_string = self.get_completion(self.prompt + text)
        logger.info("original: %s", text)
        logger.info("response: %s", json_string)
        if json_string == "":
            self.pre_selected_text = ""
            self.isSetText = False
            return

        jsonContent = json.loads(json_string)

        html_text = self.json_to_html(jsonContent,text)
        return html_text
    def set_text(self, original_text):
        logging.debug("set_text is called!")
        self.isSetText= True
        print("process!...")

        display_html = self.process_text(original_text)
        # plz help me to address this sentence's grammar error,if it exists.i will very感激。
        self.pre_selected_text = original_text
        self.text_browser.setHtml(display_html)
        self.isSetText = False

    def get_completion(self, prompt, model="gpt-3.5-turbo", temperature=0):
        """
        该函数返回一个json文件,如果chatgpt并没有生成合适的json文件，那么就返回""
        :param prompt:
        :param model:
        :param temperature:
        :return:
        """
        messages = [{"role": "user", "content": prompt}]
        try:
            response = openai.ChatCompletion.create(
                model=model,
                messages=messages,
                temperature=temperature)

            json_text = response.choices[0].message["content"]
            json_match_pattern = r'```json\s+(.*?)\s+```'
            json_matches = re.findall(json_match_pattern, json_text, re.DOTALL)# FIXME 假设只有一个，如果又多个说明生成的不对。
            if json_matches == [] or "correct_sentence" not in json_matches[0]:#REVIEW 这个correct_sentence还是必须生成的
                raise MyGeneratorJosnError("抱歉~我脑子笨未成功生成高质量答案，再试一下吧...")

            return json_matches[0]
        except MyGeneratorJosnError as e:
            logger.error(str(e))
            # 创建一个消息框
            message_box = QMessageBox(self)
            message_box.setWindowTitle("Message")
            #message_box.setText("请确保你输入的api-key正确！")
            message_box.setText(str(e))
            message_box.exec_()
            #TODO 这里可以做个操作，让主界面也给隐藏掉
            return ""
        except :
            # 创建一个消息框
            message_box = QMessageBox(self)
            message_box.setWindowTitle("Message")
            #message_box.setText("请确保你输入的api-key正确！")
            message_box.setText("请确保你输入的api-key，网络环境等正确！")
            message_box.exec_()


            return ""
    def closeEvent(self, event):
        # 窗口关闭事件处理程序
        print("close event!")
        self.hide()
        event.ignore()
    def showEvent(self, event):
        # 获取当前鼠标位置
        cursor_pos = QCursor.pos()
        print("here!")
        # 设置窗口位置为当前鼠标位置的上方
        cur_y =cursor_pos.y() - self.height()-80 #默认在上方
        if cur_y < 0:
            cur_y = cursor_pos.y() +80 #在下方生成
        self.move(cursor_pos.x(),cur_y )  # 在下方留出一定的空间

        # 调用父类的 showEvent
        super().showEvent(event)
    def handle_tray_activated(self, reason):
        if reason == QSystemTrayIcon.Trigger:
            # 单击系统托盘图标恢复窗口显示
            self.showNormal()
            self.activateWindow()
    def handle_action_config(self):
        # 创建一个消息框
        message_box = QMessageBox(self)
        message_box.setWindowTitle("info")
        message_box.setText("尚未开发，敬请期待~！")
        message_box.exec_()

class KeyboardListenerThread(QThread):
    def __init__(self,window:TextPopupWindow):
        QThread.__init__(self)
        self.window = window
        self.keyControler = keyboard.Controller()


    def run(self):
        #you are a very smart friend!
        def on_process():
            #print(key, "is press!")

            if self.window.isSetText:
                print("正在发送请求。。。请稍后")
                # TODO 可能有更好的解决方案，这里做的操作是，如果当前已经向openai发送了请求，那么就不再检测了
                return True
            print(f"热键被同时按下")
            self.window.processFlag = True

            return True
        # 启动键盘监听器
        hotkey = keyboard.GlobalHotKeys({
            self.window.hot_key: on_process})
        hotkey.start()
        hotkey.wait()
        hotkey.join()

class getMessageThread(QThread):
    text_selected = pyqtSignal(str)

    def __init__(self,window:TextPopupWindow):
        QThread.__init__(self)
        self.window = window


    def run(self):
       while(1):
           if self.window.processFlag:
               time.sleep(0.1)#等待热键释放alt+q
               self.window.processFlag = False
               # 模拟按下 Ctrl+C
               # TODO 还是没有模拟成功:<
               kb.press("ctrl")
               kb.press("c")
               time.sleep(0.01)
               kb.release("c")
               kb.release("ctrl")

               selected_text = get_selected_text()
               # if selected_text == window.pre_selected_text:
               #     #其实这里有两个好处，一个是减少查询，二个是呼出主界面在对应的位置.
               #     logger.info("您已经查询过了: %s",selected_text)
               #     return True
               # print(selected_text)
               logger.info("select text: %s", selected_text)
               if selected_text and len(selected_text) <= self.window.max_token:
                   self.text_selected.emit(selected_text)  # TODO 否则的话可以给一个信息框提示以下吧
               else:
                   logger.info("当前粘贴板内并无内容或内容过长！")
           else:
               time.sleep(0.01)


if __name__ == "__main__":
    # 启用高DPI支持
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
    app = QApplication(sys.argv)
    config_openai(api_key)

    #
    print("start!")
    # 创建窗口对象并连接信号
    window = TextPopupWindow()
    window.setWindowTitle("chatGPT Writer Assitant")
    window.resize(800, 300)
    # 创建键盘监听线程
    keyboard_listener_thread = KeyboardListenerThread(window)
    keyboard_listener_thread.start()

    get_message_thread = getMessageThread(window)
    get_message_thread.start()
    get_message_thread.text_selected.connect(window.set_text)
    get_message_thread.text_selected.connect(window.show)
    sys.exit(app.exec_())
