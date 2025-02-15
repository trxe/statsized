import logging


class Slogger:
    logger = None

    @classmethod
    def init(cls, name=__name__):
        formatter = logging.Formatter(fmt="%(asctime)s - %(levelname)s - %(module)s - %(message)s")

        handler = logging.StreamHandler()
        handler.setFormatter(formatter)

        cls.logger = logging.getLogger(name)
        cls.logger.setLevel(logging.DEBUG)
        cls.logger.addHandler(handler)

    @classmethod
    def log(cls, msg, level=logging.INFO):
        if not cls.logger:
            cls.init()
        cls.logger.log(level, msg)
