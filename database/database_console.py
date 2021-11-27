import time
from config import Logger
from importlib import import_module


def database_console():
    # start = time.time()

    mongodb_module = import_module("database.backends.mongo_database")
    # mongodb_module.update_myworld_wealth()
    mongodb_module.dump_data_elastic()

    # mysql_module = import_module("database.backends.mysql_database")
    # mysql_module.dump_data_out()

    # logger = Logger(level='warning').logger
    # logger.info("Time costs: {0}".format(time.time() - start))


if __name__ == '__main__':
    database_console()
