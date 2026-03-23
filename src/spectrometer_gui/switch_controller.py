import clr


class SwitchController:
    def __init__(self):
        self._status = None  # Replace later with a better method
        self.initialized = False

    def initialize(self, config):
        clr.AddReference("C:\\Windows\\SysWOW64\\mcl_RF_Switch_Controller_NET45.dll")
        from mcl_RF_Switch_Controller_NET45 import USB_RF_SwitchBox

        self._MyPTE1 = USB_RF_SwitchBox()
        self._MyPTE2 = USB_RF_SwitchBox()

        self._response = self._MyPTE1.Connect()
        print(self._response)

        self._conn_status = self._MyPTE1.GetUSBConnectionStatus()
        print(self._conn_status)

        self.initialized = True

    def is_initialized(self) -> bool:
        return self.initialized  # TODO: Verify the connection is still open?

    def set_switch_cavity(self):
        self._status = self._MyPTE1.Set_Switch("A", 1)

    def set_switch_freq(self):
        self._status = self._MyPTE1.Set_Switch("A", 0)

    def get_status(self):
        return self._status
