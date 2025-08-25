import logging
from datetime import datetime
import os

class LogGen:
    @staticmethod
    def loggen():
        log_dir = os.path.join(os.path.abspath(os.curdir), 'log')
        os.makedirs(log_dir, exist_ok=True)

        log_format = "%(asctime)s [%(levelname)s] %(message)s"
        log_filename = datetime.now().strftime("%Y_%m_%d_%H_%M%S.log")
        log_path = os.path.join(log_dir, log_filename)

        logger = logging.getLogger("customLogger")
        logger.setLevel(logging.INFO)

        # 핸들러가 없을 때만 추가 (중복 방지)
        if not logger.handlers:
            fileHandler = logging.FileHandler(log_path, encoding="utf-8")
            fileHandler.setFormatter(logging.Formatter(log_format))
            logger.addHandler(fileHandler)

        return logger
