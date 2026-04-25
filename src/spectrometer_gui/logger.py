import logging


class CustomLogger:
    def __init__(self, name="grugui", level=logging.INFO):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        self.formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s: %(message)s"
        )

        self.file_handler = logging.FileHandler(
            "test.log"
        )  # Change later to path stored in settings
        self.file_handler.setFormatter(self.formatter)

        self.console_handler = logging.StreamHandler()
        self.console_handler.setFormatter(self.formatter)

        self.logger.addHandler(self.file_handler)
        self.logger.addHandler(self.console_handler)
