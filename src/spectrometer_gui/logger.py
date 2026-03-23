import logging

logger = logging.getLogger()
logger.setLevel(logging.debug)

file_handler = logging.FileHandler("test.log") # Change later to path stored in settings
file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s: %(message)s"))

console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s: %(message)s"))

logger.addHandler(file_handler)
logger.addHandler(console_handler)