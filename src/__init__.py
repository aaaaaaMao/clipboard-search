import logging
import os
import json

logging.basicConfig(
    format='%(levelname)s - %(asctime)s - %(message)s',
    filename='app.log',
    filemode='a',
    encoding='utf8',
    level=logging.INFO
)

config = {}
word_list_style_sheet = ''


def load_config(file: str):
    global config
    with open(file, 'r', encoding='utf8') as f:
        config = json.load(f)


def init():
    cwd = os.getcwd()
    config_file = os.path.join(cwd, './config.json')
    data_dir = os.path.join(cwd, './data')

    load_config(config_file)

    if not os.path.exists(data_dir):
        os.mkdir(data_dir)

    global word_list_style_sheet
    style_sheet_file = os.path.join(
        os.getcwd(), './data/dictionary/db/PJE4.css')
    if os.path.exists(style_sheet_file):
        with open(style_sheet_file, 'r', encoding='utf8') as f:
            word_list_style_sheet = f.read()


init()
