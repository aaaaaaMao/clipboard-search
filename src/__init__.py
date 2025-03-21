import logging
from logging.handlers import TimedRotatingFileHandler
import os

from src.config import ConfigManager

cwd = os.getcwd()

for dir in ['logs', 'data']:
    full_dir = os.path.join(cwd, dir)
    if not os.path.exists(full_dir):
        os.makedirs(full_dir)

handler = TimedRotatingFileHandler(
    filename='logs/app.log',
    when='midnight',
    interval=1,
    backupCount=7
)

logging.basicConfig(
    format='%(levelname)s - %(asctime)s - %(message)s',
    encoding='utf8',
    level=logging.INFO,
    handlers=[handler]
)

config_manager = ConfigManager()
config = config_manager.config

word_list_style_sheet = ''

style_sheet_file = os.path.join(
    os.getcwd(), './data/dictionary/db/PJE4_2.css')
if os.path.exists(style_sheet_file):
    with open(style_sheet_file, 'r', encoding='utf8') as f:
        word_list_style_sheet = f.read()
