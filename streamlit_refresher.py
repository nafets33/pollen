from random import randint
import time
import os
# def refresher(seconds):
#     x = 0
#     while True:
#         mainDir = os.path.dirname(__file__)
#         filePath = os.path.join(mainDir, 'test.py')
#         x += 1
#         # write (or upload) your streamlit file
#         with open(filePath, 'w') as f:
#             f.write(f'import streamlit as st\nst.title("# {x}")')
#         time.sleep(seconds)
# refresher(1)

def refresher(seconds):
    x = 0
    while True:
        mainDir = os.path.dirname(__file__)
        filePath = os.path.join(mainDir, 'test.py')
        x += 1
        # write (or upload) your streamlit file
        with open(filePath, 'r') as input:
            output = open(filePath, 'w')
            output.write(input.read())
        time.sleep(seconds)
refresher(10)