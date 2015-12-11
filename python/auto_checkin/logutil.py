import logging
import os

# create parent directory if needed
if not os.path.exists('./log'):
    os.mkdir('log')

logging.basicConfig(
    filename='log/running.log', filemode='a+', level=logging.DEBUG,
    format='- %(levelname)s | %(module)s | %(asctime)s -: %(message)s')

def get_logger():
    return logging
