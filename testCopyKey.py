#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@Project ：grammarCheckerbasedOpenai 
@File ：testCopyKey.py
@Author ：HuntingGame
@Date ：2023-06-11 10:59 
C'est la vie!!! enjoy ur day :D

测试模拟复制粘贴的热键
'''
import time

import keyboard
import clipboard


def simulate_copy_paste():
    # 模拟按下 Ctrl+C
    keyboard.press_and_release('ctrl+c')

    # 打印剪贴板内容
    # 延迟一段时间，等待剪贴板内容的更新
    time.sleep(0.1)
    clipboard_content = clipboard.paste()
    print("剪贴板内容:", clipboard_content)




# 监听 Ctrl+V 组合键
keyboard.add_hotkey('ctrl+1', simulate_copy_paste)

# 开始监听键盘事件
keyboard.wait('esc')

