import sys
import os
import gc
import importlib


current_folder = os.path.dirname(os.path.abspath(__file__))
if current_folder not in sys.path:
    sys.path.insert(0, current_folder)


modules_to_clear = ["style", "UI", "logic"]
for mod in modules_to_clear:
    if mod in sys.modules:
        del sys.modules[mod]
gc.collect()


try:
    import style  
    import UI
    import logic
    
    
    importlib.reload(style)
    importlib.reload(UI)
    importlib.reload(logic)
    
except Exception as e:
    print(f"[ERROR] Failed to load Plugin Manager modules: {e}")

from PySide6.QtWidgets import QApplication, QListWidgetItem
from PySide6.QtCore import Qt
from qtmax import GetQMaxMainWindow
from pymxs import runtime as rt


from UI import MainUI
from logic import PluginManagerLogic

class AppController(MainUI):
    def __init__(self, parent=None):
        super(AppController, self).__init__(parent)
        self.setStyleSheet(style.STYLE_MAIN)
        self.logic = PluginManagerLogic()
        self.init_content(max_version=self.logic.max_version) 
        self.load_data()

        self.show_all_cb.stateChanged.connect(self.load_data)
        self.btn_save.clicked.connect(self.apply_settings)
        self.btn_launch.clicked.connect(self.apply_and_close)
        self.btn_add_profile.clicked.connect(self.create_profile)
        self.btn_del_profile.clicked.connect(self.delete_profile) 
        self.profile_list.itemClicked.connect(self.select_profile)
        self.search_input.textChanged.connect(self.filter_plugins)

    def load_data(self):
        self.plugin_list.clear()
        plugins = self.logic.get_all_plugins()
        show_advanced = self.show_all_cb.isChecked() 
        
        for p in plugins:
            is_core_plugin = (p['source'] == "Plugins")
            is_system_subfile = any(x in p['path'].lower() for x in ["\contents", "civilview", "alembic", "maxfluid"])

            if not is_core_plugin and not show_advanced and is_system_subfile:
                continue
                
            display_text = f"[{p['source']}] {p['name']}"
            item = QListWidgetItem(display_text)
            item.setData(Qt.UserRole, p['path'])
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Checked if p['is_enabled'] else Qt.Unchecked)
            
            if is_system_subfile:
                item.setForeground(Qt.darkGray)
                
            self.plugin_list.addItem(item)

    def apply_settings(self):
        states = {}
        for i in range(self.plugin_list.count()):
            item = self.plugin_list.item(i)
            current_path = item.data(Qt.UserRole)
            should_be_enabled = (item.checkState() == Qt.Checked)
            
            new_path = self.logic.toggle_plugin(current_path, should_be_enabled)
            item.setData(Qt.UserRole, new_path)
            states[new_path] = should_be_enabled
            
        self.logic.save_to_ini(states)
        rt.displayTempPrompt("Disk & INI Updated!", 3000)
        self.load_data() 

    def apply_and_close(self):
        self.apply_settings()
        self.close()

    def create_profile(self):
        name = self.profile_input.text()
        if not name: return
        
        active_paths = [self.plugin_list.item(i).data(Qt.UserRole) 
                        for i in range(self.plugin_list.count()) 
                        if self.plugin_list.item(i).checkState() == Qt.Checked]
        
        self.logic.save_profile(name, active_paths)
        if self.profile_list.findItems(name, Qt.MatchExactly) == []:
            self.profile_list.addItem(name)
        self.profile_input.clear()

    def select_profile(self, item):
        profiles = self.logic.load_profiles()
        active_paths = profiles.get(item.text(), [])
        
        for i in range(self.plugin_list.count()):
            p_item = self.plugin_list.item(i)
            if p_item.data(Qt.UserRole) in active_paths:
                p_item.setCheckState(Qt.Checked)
            else:
                p_item.setCheckState(Qt.Unchecked)

    def delete_profile(self):
        current_item = self.profile_list.currentItem()
        if not current_item: return
        
        name = current_item.text()
        profiles = self.logic.load_profiles()
        if name in profiles:
            del profiles[name]
            with open(self.logic.profiles_path, 'w') as f:
                import json
                json.dump(profiles, f)
        self.load_data()

    def filter_plugins(self, text):
        for i in range(self.plugin_list.count()):
            item = self.plugin_list.item(i)
            item.setHidden(text.lower() not in item.text().lower())

def main():
    main_win = GetQMaxMainWindow()
    for widget in main_win.findChildren(MainUI):
        widget.close()
        widget.deleteLater()

    gui = AppController(main_win)
    gui.show()

if __name__ == "__main__":
    main()