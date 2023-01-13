import logging


def init_logger(logger, filename):
    # set Logging Format
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s', datefmt="%d-%m-%Y %H:%M:%S")

    # adding file handler
    fileHandler = logging.FileHandler(filename)
    fileHandler.setFormatter(formatter)

    logger.addHandler(fileHandler)
