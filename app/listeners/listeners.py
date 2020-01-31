import logging


fmt = "%(asctime)s %(message)s"
logger = logging.getLogger("testqueue")
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='testqueue.log', mode='a', encoding='utf-8', delay=False)
handler.setFormatter(logging.Formatter(fmt))
logger.addHandler(handler)


def testqueue(**kwargs):
    logger.debug(kwargs)
    logger.debug("testqueue in!")