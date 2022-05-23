import os, pathlib, shutil
import RLPy, PySide2
from PySide2 import QtWidgets

import PySide2.QtWebSockets as qtws
from PySide2.QtGui import QDesktopServices
from shiboken2 import wrapInstance
from PySide2.QtCore import Qt, QObject, QTimer, QUrl

path_cache = None

current_path = os.path.dirname(__file__)
ap_path =  os.path.dirname(RLPy.RApplication.GetProgramPath())

ui = {}

event_callback = None
event_callback_id = None

#os.system('"explorer.exe " + exp_template')

'''
print (exp_template)
my_list = os.listdir(exp_template)
print (my_list)
'''

class DialogEventCallback(RLPy.RDialogCallback):
    def __init__(self):
        RLPy.RDialogCallback.__init__(self)

    def OnDialogClose(self):
        global ui
        global event_callback
        global event_callback_id

        #urlcleanup()
        #ui.pop('window', None)
        #ui.pop('ani_window', None)
        #ui.pop('status', None)
        #ui.pop('warning', None)
        #ui.pop('avatar_combo', None)
        #ui.pop('export_button', None)

        event_callback = None
        if event_callback_id is not None:
            RLPy.REventHandler.UnregisterCallbacks([event_callback_id])
            event_callback_id = None

        return True

class OnChangeEventsCallback(RLPy.REventCallback):
    def __init__(self):
        RLPy.REventCallback.__init__(self)

    def OnFileLoaded(self, nFileType):
        pass

    def OnObjectAdded(self):
        pass

    def OnObjectDeleted(self):
        pass

    def OnUndoRedoDone(self):
        pass

    def OnObjectDataChangedWithType(self, nDataType):
        pass

    def OnHierarchyChanged(self):
        pass
        
    def OnObjectSelectionChanged(self):
        pass
        #update_selection()

def _process_facial_data_nfs(face_component,):
    facial_data = {}
    exp_names = face_component.GetExpressionNames("")
    if face_component and len(exp_names):
        current_time = RLPy.RGlobal.GetTime()
        empty_name = []
        exp_weight = face_component.GetExpressionWeights(current_time, empty_name)
        facial_data = { 
            "Names": exp_names, 
            "Weights": exp_weight }
    return facial_data

def save():
    #print (_path)
    global path_cache
    
    avatar_list = RLPy.RScene.GetAvatars()
    
    if (len(avatar_list) == 0):
        return
    
    avatar = avatar_list[0]
    face_component = avatar.GetFaceComponent()
    uid = face_component.GetExpressionSetUid()
    exp_template = os.path.dirname(ap_path)+"\\Program\\Assets\\Share\\FacialSystem\\"+uid+"\\Expression\\"
    
    icon_file = os.path.dirname(ap_path)+"\\Program\\Assets\\Share\\FacialSystem\\"+uid+"\\Expression\\01-Happy\\icons\\default.png"
    
    facial_data = _process_facial_data_nfs(face_component)
    
    #print (facial_data)
    
    dialog = QtWidgets.QFileDialog()
    dialog.setDefaultSuffix('ini')
    dialog.setAcceptMode(QtWidgets.QFileDialog.AcceptSave)
    dialog.setNameFilters(['ini (*.ini)'])
    
    if (path_cache==None):
        dialog.setDirectory(exp_template)
    else:
        dialog.setDirectory(path_cache)
    
    if dialog.exec_() == QtWidgets.QDialog.Accepted:
        path_cache = dialog.selectedFiles()[0]
        with open(dialog.selectedFiles()[0], 'w') as f:
            f.write("[Expression]\n")
            name = facial_data["Names"]
            data = facial_data["Weights"]
            #print (data)
            for i in range(len(name)):
                f.write(name[i]+"="+str(int(data[i]*100))+"\n")
                
            f.write("\n")
            f.write("[ExpressionWeight]\n")
            f.write("SliderValue=100\n")
        try:
            icon_folder = pathlib.Path(dialog.selectedFiles()[0]).parent.resolve() / "icons"
            os.mkdir(icon_folder)
        except:
            pass
        
        icon_name = (pathlib.Path(dialog.selectedFiles()[0]).stem)
        shutil.copyfile(icon_file, icon_folder / (icon_name + ".png"))

    '''
    else:
        RLPy.RUi.ShowMessageBox(
        "Error Message",
        "Failed to save the file.",
        RLPy.EMsgButton_Ok
        )
    '''

def create_window():
    global ui

    ui["window"] = RLPy.RUi.CreateRDockWidget()
    '''
    ui["window"].SetAllowedAreas(
        RLPy.EDockWidgetAreas_RightDockWidgetArea +
        RLPy.EDockWidgetAreas_LeftDockWidgetArea
    )
    '''
    ui["window"].SetWindowTitle("Save File")

    # Create layout widget
    qt_window = wrapInstance(
        int(ui["window"].GetWindow()),
        QtWidgets.QDockWidget
    )
    qt_dialog = QtWidgets.QWidget()
    qt_dialog.setLayout(QtWidgets.QVBoxLayout())
    qt_dialog.setMinimumHeight(280)
    qt_dialog.setMinimumWidth(400)

    ui["export_button"] = QtWidgets.QPushButton("Save")
    
    ui["export_button"].clicked.connect(
        save
    )
    
    ui["export_button"].setFixedHeight(28)

    #hlayout.addWidget(ui["export_button"])

    #vlayout.addWidget(help_label)
    #vlayout.addLayout(hlayout)
    #help_box.setLayout(vlayout)
    qt_dialog.layout().addWidget(ui["export_button"])

    qt_window.setWidget(qt_dialog)

    ui["window"].Show()


def show_window():
    global ui
    global event_callback
    global event_callback_id

    if event_callback is None:
        event_callback = OnChangeEventsCallback()
        event_callback_id = RLPy.REventHandler.RegisterCallback(event_callback)

    if "window" in ui:
        if ui["window"].IsVisible():
            pass
        else:
            ui["window"].Show()
    else:
        create_window()
        ui["dialog_events"] = DialogEventCallback()
        ui["window"].RegisterEventCallback(ui["dialog_events"])
        
    #update_selection()

def initialize_plugin():
    # Create Pyside interface with iClone main window
    ic_dlg = wrapInstance(int(RLPy.RUi.GetMainWindow()), QtWidgets.QMainWindow)

    plugin_menu = ic_dlg.menuBar().findChild(QtWidgets.QMenu, "Exp_temp")
    if plugin_menu is None:  # Check if the menu item exists

        # Create Pyside layout and attach it to the Plugins menu
        plugin_menu = wrapInstance(
            int(RLPy.RUi.AddMenu("Exp_temp", RLPy.EMenu_Plugins)),
            QtWidgets.QMenu
        )
        plugin_menu.setObjectName("Exp_temp")

    # Check if the menu action already exists
    menu_actions = plugin_menu.actions()
    for i in range(len(menu_actions)):
        if menu_actions[i].text() == "Save":
            # Remove duplicate actions
            plugin_menu.removeAction(menu_actions[i])

    # Set up the menu action
    menu_action = plugin_menu.addAction("Save")
    menu_action.triggered.connect(show_window)
    

def run_script():
    initialize_plugin()
