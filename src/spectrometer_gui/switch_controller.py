import clr

clr.AddReference('C:\\Windows\\SysWOW64\\mcl_RF_Switch_Controller_NET45.dll')

from mcl_RF_Switch_Controller_NET45 import USB_RF_SwitchBox

class SwitchController:
    def __init__(self):
        self.__status = None # Replace later with a better method

        self.__MyPTE1 = USB_RF_SwitchBox()
        self.__MyPTE2 = USB_RF_SwitchBox()

        self.__response = self.__MyPTE1.Connect()
        print(self.__response)

        self.__conn_status = self.__MyPTE1.GetUSBConnectionStatus()
        print(self.__conn_status)


    def set_switch_cavity(self):
        self.__status = self.__MyPTE1.Set_Switch("A", 1)

    def set_switch_freq(self):
        self.__status = self.__MyPTE1.Set_Switch("A", 0)

    def get_status(self):
        return self.__status