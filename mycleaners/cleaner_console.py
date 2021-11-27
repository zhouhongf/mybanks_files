import os
import time
from config import CONFIG
from config import Logger
from importlib import import_module


def file_name(file_dir=os.path.join(CONFIG.BASE_DIR, 'mycleaners/cleaner_banks')):
    all_files = []
    for file in os.listdir(file_dir):
        if file.endswith('_cleaner.py'):
            all_files.append(file.replace('.py', ''))
    return all_files


def cleaner_console():
    start = time.time()
    all_files = file_name()

    for cleaner in all_files:
        cleaner_module = import_module("mycleaners.cleaner_banks.{}".format(cleaner))
        cleaner_module.start()

    logger = Logger(level='warning').logger
    logger.info("Time costs: {0}".format(time.time() - start))


if __name__ == '__main__':
    cleaner_console()
