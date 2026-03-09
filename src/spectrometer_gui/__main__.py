from PySide6.QtWidgets import QApplication

import asyncio
import sys
from qasync import QEventLoop

from gui.main_window import MainWindow

async def main(app):
    app_close_event = asyncio.Event()
    app.aboutToQuit.connect(app_close_event.set)

    main_window = MainWindow(app)
    main_window.show()

    await app_close_event.wait()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    asyncio.run(main(app), loop_factory=QEventLoop)
