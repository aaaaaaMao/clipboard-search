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


init()
