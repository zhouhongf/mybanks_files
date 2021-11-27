import os
import time
from config import CONFIG
from config import Logger
from importlib import import_module


def file_name(file_dir=os.path.join(CONFIG.BASE_DIR, 'myanalyzers/analyzer_banks')):
    all_files = []
    for file in os.listdir(file_dir):
        if file.endswith('_analyzer.py'):
            all_files.append(file.replace('.py', ''))
    return all_files


def analyzer_console():
    start = time.time()
    all_files = file_name()

    for analyzer in all_files:
        analyzer_module = import_module("myanalyzers.analyzer_banks.{}".format(analyzer))
        analyzer_module.start()

    logger = Logger(level='warning').logger
    logger.info("Time costs: {0}".format(time.time() - start))


if __name__ == '__main__':
    analyzer_console()
