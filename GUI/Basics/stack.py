import PyQt5.QtWidgets as QtWidgets

class AssetCreationWindow(QtWidgets.QMainWindow):

    def __init__(self, controller):
        super(AssetCreationWindow, self).__init__()
        self.controller = controller
        self.create_content()
        self.show()

def create_content(self):

# creating main container-frame, parent it to QWindow
    self.main_CF = QtWidgets.QFrame(self)
    self.main_CF.setStyleSheet('background-color: rgba(150, 0, 0, 1);')
    self.setCentralWidget(self.main_CF)
# creating layout and parent it to main container
# is it correct, that main_CL now manages children of main_CF ?
    self.main_CL = QtWidgets.QVBoxLayout(self.main_CF)


# creating the first subcontainer + layout, parenting it
    asset_CGF = QtWidgets.QFrame(self.main_CF)
    self.main_CL.addWidget(asset_CGF)
    asset_CGF.setStyleSheet('background-color: rgba(0, 150, 0, 1);')
    asset_CGL = QtWidgets.QHBoxLayout(asset_CGF)

# creating label and lineEdit, both are supposed to be on top of asset_CGF
    asset_label = QtWidgets.QLabel("Assetname: ", asset_CGF)
    asset_CGL.addWidget(asset_label)
    asset_name = QtWidgets.QLineEdit("MyNewAsset", asset_CGF)
    asset_CGL.addWidget(asset_name)

# doing the same with a second container
    department_CGF = QtWidgets.QFrame(self.main_CF)
    self.main_CL.addWidget(department_CGF)
    department_CGF.setStyleSheet('background-color: rgba(0, 0, 150, 1);')
    department_CGL = QtWidgets.QHBoxLayout(department_CGF)

    department_label = QtWidgets.QLabel("Department: ", department_CGF)
    department_CGL.addWidget(department_label)

    department_names = QtWidgets.QComboBox(department_CGF)
    department_CGL.addWidget(department_names)