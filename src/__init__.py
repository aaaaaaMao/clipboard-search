import logging

logging.basicConfig(
    format='%(levelname)s - %(asctime)s - %(message)s',
    filename='app.log',
    filemode='a',
    encoding='utf8',
    level=logging.INFO
)
