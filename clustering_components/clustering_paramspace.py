# NAME
#
#        clustering_paramspace
#
# DESCRIPTION
#
#       'clustering_paramspace' contains the QTwidget that allows the user to select the parameters for the clustering
#
# AUTHORS
#
#       Raphaël AGATHON - Maxime CLUCHLAGUE - Graziella HUSSON - Valentina ZELAYA
#       Marie ADLER - Aurélien BENOIT - Thomas GRASSELLINI - Lucie MARTIN

from PyQt4 import QtGui
from PyQt4.QtCore import Qt, QSize

import gc

from BrainMapper import *
from functools import partial

class InfoButton(QtGui.QPushButton):
    def __init__(self,widget,layout):
        super(InfoButton,self).__init__(parent=widget)
        self.message = ""
        self.setFixedSize(QSize(20, 20))
        self.setText("?")
        self.clicked.connect(self.open)
        layout.addWidget(self)

    def setMessage(self,message):
        self.message = message

    def open(self):
        method_dict = get_selected_clustering_info()
        QtGui.QMessageBox.information(self,"Information",self.message,"ok")


class ParametersBox(QtGui.QGroupBox):
    """ A class implementing the parameters Box"""
    def __init__(self, parameters_dict=None):
        super(ParametersBox, self).__init__("Parameters")
        self.user_params = {}
        self.vbox = QtGui.QVBoxLayout()
        self.vbox.setContentsMargins(0, 0, 0, 0)

        if parameters_dict is not None:

            for param_name in parameters_dict.keys():

                particular_param_dict = parameters_dict[param_name]
                param = ParameterNameAndValue(param_name, particular_param_dict["type"],
                                                                   particular_param_dict["default"],
                                                                   particular_param_dict["param_info"])

                self.vbox.addWidget(param)
        else:
            placeholder_label = QtGui.QLabel("No parameters to show")
            self.vbox.addWidget(placeholder_label)

        self.setLayout(self.vbox)

    def save_user_params(self):
        """
        Save user parameters
        """
        for i in reversed(range(self.vbox.count())):
            if self.vbox.itemAt(i).widget() is not None :
                (param_name, param_value) = self.vbox.itemAt(i).widget().get_name_value_pair()
                self.user_params[param_name] = param_value

    def get_user_params(self):
        """
        Obtains user parameters
        """
        self.save_user_params()
        if self.user_params is not None :
            return self.user_params
        else:
            return None


class ParameterNameAndValue(QtGui.QGroupBox):
    """
     A class for parameter labels (simplifies the clustering method dictionary building process with user input)
    """
    def __init__(self, param_name, param_type, param_default_value, param_info):
        super(ParameterNameAndValue, self).__init__()
        self.setMaximumSize(QSize(290, 16777215))
        self.grid = QtGui.QGridLayout()
        self.grid.setContentsMargins(0, 9, 9, 0)

        self.help_button = InfoButton(self,self.grid)
        self.help_button.setMessage(param_info)
        # -- Parameter's name ------
        self.param_name_label = QtGui.QLabel(param_name)
        self.param_name_label.setMinimumSize(QSize(100, 15))
        #self.param_name_label.setMaximumSize(QSize(100, 21))

        # --- Parameter type control ----
        if type(param_type) is list:
            # self.param_value_input = QtGui.QToolButton()
            # self.param_value_input.setText(str(param_default_value))
            # self.param_value_input.setPopupMode(QtGui.QToolButton.MenuButtonPopup)
            #
            # param_value_chooser = QtGui.QMenu()
            #
            # for param_value_choice in param_type:
            #     param_choice = QtGui.QAction(param_value_choice, self)
            #     param_choice.triggered.connect(self.choice_clicked)
            #     param_value_chooser.addAction(param_choice)
            #
            # self.param_value_input.setMenu(param_value_chooser)
            self.param_value_input = QtGui.QComboBox()
            self.param_value_input.setObjectName("param_value_input")
            for param_value_choice in param_type:
                self.param_value_input.addItem(param_value_choice)



        else:
            self.param_value_input = QtGui.QLineEdit()
            self.param_value_input.setText(str(param_default_value))

        # self.param_value_input.setToolTip(param_info)
        self.param_value_input.setStatusTip(param_info)
        self.param_value_input.setMinimumSize(QSize(150, 19))
        self.param_value_input.setSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Maximum)

        self.grid.addWidget(self.help_button,0,0)
        self.grid.addWidget(self.param_name_label, 0, 1)
        self.grid.addWidget(self.param_value_input, 0, 2)
        self.setLayout(self.grid)
        #self.pushButton_info = QtGui.QPushButton()
        #self.pushButton_info.setObjectName(_fromUtf8("pushButton_show"))
        #self.pushButton_info.clicked.connect(self.open)
    def choice_clicked(self):
        """
        Change label based on what button was pressed
        """
        choice = self.sender()
        if isinstance(choice, QtGui.QAction):
            self.param_value_input.setText(choice.text())

    def update_param_value_label(self, new_user_value):
        self.param_value_input.setText(new_user_value)

    def get_name_value_pair(self):
        if type(self.param_value_input)==QtGui.QComboBox:
            return str(self.param_name_label.text()), str(self.param_value_input.currentText())
        else:
            return str(self.param_name_label.text()), str(self.param_value_input.text())


# A custom widget to implement the script environment
class ScriptEnvironment(QtGui.QWidget):

    def __init__(self, title_style):
        super(ScriptEnvironment, self).__init__()

        container_box = QtGui.QVBoxLayout()

        scriptEnv_title = QtGui.QLabel('Script Environment')
        scriptEnv_title.setStyleSheet(title_style)

        editor = QtGui.QVBoxLayout()
        self.edit_input = QtGui.QTextEdit()

        editor.addWidget(scriptEnv_title)
        editor.addWidget(self.edit_input)

        container_box.addLayout(editor)

        # Add the layout to script widget
        self.setLayout(container_box)


class ClusteringParameters(QtGui.QWidget):
    """
    A custom QWidget for clustering algorithms explanation and parameters display
    """

    # CONSTRUCTOR
    def __init__(self):

        super(ClusteringParameters, self).__init__()

        # I chose to use a dictionary : the implemented clustering algorithms will give an
        # 'expected parameter dictionnary' (json file in resources)
        # For example : {"distance":None, "k":None}, could be the dictionary given by the Kmeans method,
        # and it will expect this dictionary to be completed by the user

        self.parameters_dict = None
        self.clustering_name = "None selected yet"
        self.clustering_info = "Please select a classifier from the top menu"

        self.container_box = None
        self.clust_title = None
        self.param_box = None

        self.container_box = QtGui.QVBoxLayout()
        self.container_box.setContentsMargins(0, 0, 0, 0)
        self.container_box.setAlignment(Qt.AlignTop)

        self.setLayout(self.container_box)

    def update_clustering_info_and_params(self, selected_clustering_name):
        """
        Update the algorithm description and parameters based on the selected algorithm

        Arguments :
            selected_clustering_name{string} -- The selected clustering method's name
        """
        # Call controller to get the currently selected parameters' dictionary
        method_dict = get_selected_clustering_info()

        # If controller did not find a match in methods dictionary
        if method_dict is None:
            err = QtGui.QMessageBox.critical(self, "Error",
                                             "No clustering method has been selected yet")
            err.setParent(None)
            err.deleteLater()   # Saves memory !

        # Else update this custom QWidget
        else:
            self.clustering_name = selected_clustering_name
            self.clustering_info = method_dict['algo_info'] + "\nUsecase :" + method_dict["algo_usecase"]
            self.parameters_dict = method_dict["param_list"]

            # Clean up the previous param box and the cluster labels
            for i in reversed(range(self.container_box.count())):
                self.container_box.itemAt(i).widget().setParent(None)

            gc.collect()  # DANGER : calling garbage collector

            # Add parameter box
            self.param_box = ParametersBox(self.parameters_dict) #self.param_dict has been set to method_dict["param_list"]
            self.container_box.addWidget(self.param_box)

    def export_user_params(self):
        """
        Parameters exported
        """
        if self.param_box is not None:
            return self.param_box.get_user_params()
        else: return None


# A custom widget to stack the ClusteringParameters Widget and the ScripEnvironnement Widget
class ParameterAndScriptStack(QtGui.QWidget):

    def __init__(self, title_style, clustering_chooser=None):

        super(ParameterAndScriptStack, self).__init__()
        # #print("stack")
        # Initialize a stack (pile) widget
        self.stack = QtGui.QStackedWidget()
        layout = QtGui.QVBoxLayout(self) # vertical layout
        layout.addWidget(self.stack) # stack in the vertical layout

        # Here are the custom widgets we will put on the stack
        self.clust_params_widget = ClusteringParameters()
        self.script_env_widget = ScriptEnvironment(title_style)
        # -- Add them to stack widget
        self.stack.addWidget(self.clust_params_widget)
        self.stack.addWidget(self.script_env_widget)

        self.clusteringChooser = clustering_chooser

        # Define behaviour when widget emit certain signals (see class MainView and Clustering View for more details
        #  on signals and events)

        # -- when clusteringChooser widget emits signal showClustParamsWidget, change current Widget in stack to clust params widget
        #self.clusteringChooser.
        self.clusteringChooser.showClustParamsWidget.connect(self.update_clustering_parameters)
        # -- when clusteringChooser widget emits signal showClustParamsWidget, change current Widget in stack to scrip env widget
        self.clusteringChooser.showScriptEnvWidget.connect(partial(self.stack.setCurrentWidget, self.script_env_widget))


        # Set current widget to main view by default
        #self.stack.setCurrentWidget(self.clust_params_widget)
        #rec = QtGui.QApplication.desktop().availableGeometry()
        #mainwind_h = rec.height() / 1.4
        #mainwind_w = rec.width() / 1.5
        #del rec  # Saves memory
        #self.setMaximumSize(QSize(mainwind_w / 3, mainwind_h))

    def update_clustering_parameters(self):
        """
        Update clustering parameters
        """
        self.clust_params_widget.update_clustering_info_and_params(self.clusteringChooser.get_selected_method_name())
        self.stack.setCurrentWidget(self.clust_params_widget)

    def get_user_params(self) :
        """
        Obtain clustering parameters
        """
        if self.stack.currentWidget() is not self.script_env_widget:
            return self.stack.currentWidget().export_user_params()
