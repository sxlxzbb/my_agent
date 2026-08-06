import logging
from logging import StreamHandler, Formatter

_DEFAULT_FORMAT = "%(asctime)s %(levelname)s %(name)s %(message)s"


def get_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """统一的日志器工厂：自动配置 INFO 级别与控制台 handler。

    多次调用（或模块被重复 import）不会重复添加 handler。
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    if not logger.handlers:
        handler = StreamHandler()
        handler.setFormatter(Formatter(_DEFAULT_FORMAT))
        logger.addHandler(handler)
    return logger
