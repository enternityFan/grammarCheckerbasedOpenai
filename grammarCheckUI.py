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
import os
import string
import sys
import time
from datetime import datetime

import clipboard
import markdown2
from PyQt5.QtGui import QCursor, QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextBrowser, QVBoxLayout, QMessageBox, QWidget, QSystemTrayIcon, \
    QAction, QMenu
from PyQt5.QtCore import Qt, pyqtSignal, QThread, QPoint, QRect, QEvent
from pynput import keyboard
import pyautogui
import pygetwindow as gw
import openai
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
console_handler.setLevel(logging.DEBUG)
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

text = ""
prompt = f"First of all, if there is Chinese, please help me translate Chinese into proper English, and please explain the grammatical rules contained therein :```"




def config_openai(api_key):
    openai.api_key = api_key


def get_selected_text():
    try:

        # 打印剪贴板内容
        # 延迟一段时间，等待剪贴板内容的更新
        time.sleep(0.2)
        selected_text = clipboard.paste()
        return selected_text
    except:
        return ""
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
        self.text_browser.setContentsMargins(0, 0, 120, 120)# 设置控件边界
        layout.addWidget(self.text_browser)
        # 设置主窗口的布局
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
        self.setWindowFlags(Qt.WindowStaysOnTopHint )
        self.isSetText = False

        self.drag_position = QPoint()
        self.setMouseTracking(True)  # 开启鼠标追踪
        self.resize_handle_size = 10  # 设置边缘调整大小的触发区域大小

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
        self.setConfig()
        self.tray_icon.show()

    def setConfig(self):
        self.FontSize = configReader.get_value("FontSize")
        self.hot_key = configReader.get_value("hot-key")
        self.max_token = configReader.get_value("max_token")
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
        response = self.get_completion(prompt + text + "```")
        logger.info("response: %s",response)
        if response == "":
            self.isSetText = False
            return
        diff = Redlines(text, response)
        formatted_output = markdown2.markdown(diff.output_markdown)
        formatted_output = self.setFontSize(formatted_output)
        self.text_browser.setHtml(formatted_output)
        self.isSetText = False

    def get_completion(self, prompt, model="gpt-3.5-turbo", temperature=0):
        messages = [{"role": "user", "content": prompt}]
        try:
            response = openai.ChatCompletion.create(
                model=model,
                messages=messages,
                temperature=temperature)

            return response.choices[0].message["content"]
        except:
            # 创建一个消息框
            message_box = QMessageBox(self)
            message_box.setWindowTitle("Message")
            message_box.setText("请确保你输入的api-key正确！")
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

        # 设置窗口位置为当前鼠标位置的上方
        self.move(cursor_pos.x(), cursor_pos.y() - self.height()-80)  # 在下方留出一定的空间

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
    text_selected = pyqtSignal(str)

    def __init__(self,window:TextPopupWindow):
        QThread.__init__(self)
        self.window = window


    def run(self):
#you are a very smart friend!
        def on_press(key):
            #print(key, "is press!")

            if str(key) == self.window.hot_key:
                if self.window.isSetText:
                    print("正在发送请求。。。请稍后")
                    # TODO 可能有更好的解决方案，这里做的操作是，如果当前已经向openai发送了请求，那么就不再检测了
                    return True
                print(f"热键被同时按下")
                # 模拟按下 Ctrl+C
                kb.press_and_release('ctrl+c')


                selected_text = get_selected_text()
                #print(selected_text)
                logger.info("select text: %s",selected_text)
                if selected_text and len(selected_text) <= self.window.max_token:
                    self.text_selected.emit(selected_text)#TODO 否则的话可以给一个信息框提示以下吧
                else:
                    logger.info("当前粘贴板内并无内容或内容过长！")
            return True
        # 启动键盘监听器
        with keyboard.Listener(on_press=on_press) as listener:
            listener.join()

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
    keyboard_listener_thread.text_selected.connect(window.set_text)
    keyboard_listener_thread.text_selected.connect(window.show)

    sys.exit(app.exec_())
