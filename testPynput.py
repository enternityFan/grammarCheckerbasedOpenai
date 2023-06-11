#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@Project ：grammarCheckerbasedOpenai 
@File ：testPynput.py
@Author ：HuntingGame
@Date ：2023-06-11 16:30 
C'est la vie!!! enjoy ur day :D
'''

from pynput import keyboard

def on_press(key):
    try:
        print('按下按键: {0}'.format(key.char))
    except AttributeError:
        print('按下特殊按键: {0}'.format(key))

def on_release(key):
    print('释放按键: {0}'.format(key))
    if key == keyboard.Key.esc:
        # 当按下 Esc 键时停止监听
        return False

# 创建监听器
listener = keyboard.Listener(
    on_press=on_press,
    on_release=on_release)

# 开始监听
listener.start()

# 等待监听器停止（这里是一个阻塞操作）
listener.join()
