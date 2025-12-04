import serial
import time


class VSerialPort(serial.Serial):
    def __init__(self, port_name):
        serial.Serial.__init__(self)
        # Try:
        self.baudrate = 9600
        self.timeout = 3
        self.port = port_name
        self.open()
        self.setDTR(False)
        self.flushInput()
        self.setDTR(True)
        self.write(b"ID?\r")
        response_bytes = self.read(1024)  # Total bytes expected back from return
        print(response_bytes)
        # CW mode (continuous wave)
        print("________________________________________________________")
        print(f"Serial port for Valon: {port_name} opened successfully.")
        print("________________________________________________________")
        time.sleep(0.5)
