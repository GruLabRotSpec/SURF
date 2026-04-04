import logging

class CustomLogger():
    def __init__(self):
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)

        self.file_handler = logging.FileHandler("test.log") # Change later to path stored in settings
        self.file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s: %(message)s"))

        self.console_handler = logging.StreamHandler()
        self.console_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s: %(message)s"))

        self.logger.addHandler(self.file_handler)
        self.logger.addHandler(self.console_handler)