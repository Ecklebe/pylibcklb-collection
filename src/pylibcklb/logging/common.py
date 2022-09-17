import logging


def create_logger(application_name: str, default_level=logging.NOTSET):
    # create logger
    logger = logging.getLogger(application_name)
    logger.setLevel(default_level)

    # create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    # create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # add formatter to ch
    ch.setFormatter(formatter)

    # add ch to logger
    logger.addHandler(ch)

    return logger
