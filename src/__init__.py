import logging
import os

from src.config import ConfigManager

logging.basicConfig(
    format='%(levelname)s - %(asctime)s - %(message)s',
    filename='app.log',
    filemode='a',
    encoding='utf8',
    level=logging.INFO
)

config = ConfigManager().config

word_list_style_sheet = ''

def init():
    cwd = os.getcwd()
    data_dir = os.path.join(cwd, './data')

    if not os.path.exists(data_dir):
        os.mkdir(data_dir)

    global word_list_style_sheet
    style_sheet_file = os.path.join(
        os.getcwd(), './data/dictionary/db/PJE4_2.css')
    if os.path.exists(style_sheet_file):
        with open(style_sheet_file, 'r', encoding='utf8') as f:
            word_list_style_sheet = f.read()


init()
