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

config_manager = ConfigManager()
config = config_manager.config

word_list_style_sheet = ''

cwd = os.getcwd()
data_dir = os.path.join(cwd, './data')

if not os.path.exists(data_dir):
    os.mkdir(data_dir)

style_sheet_file = os.path.join(
    os.getcwd(), './data/dictionary/db/PJE4_2.css')
if os.path.exists(style_sheet_file):
    with open(style_sheet_file, 'r', encoding='utf8') as f:
        word_list_style_sheet = f.read()
