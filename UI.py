from PySide6.QtWidgets import *
from PySide6.QtCore import Qt

class MainUI(QMainWindow):
    def __init__(self, parent=None): 
        super(MainUI, self).__init__(parent) 
        self.setWindowTitle("3DSMax Plugin Manager Pro")
        self.setMinimumSize(850, 600)
        

    

    def init_content(self, max_version="2026"):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.layout = QHBoxLayout(central_widget)

        # Left: Profiles
        self.left_col = QVBoxLayout()
        self.left_col.addWidget(QLabel("PROFILES"))
        self.profile_list = QListWidget()
        self.left_col.addWidget(self.profile_list)
        
        self.profile_input = QLineEdit()
        self.profile_input.setPlaceholderText("Profile Name...")
        
        profile_btns = QHBoxLayout()
        self.btn_add_profile = QPushButton("Create")
        self.btn_add_profile.setObjectName("CreateBtn")
        self.btn_del_profile = QPushButton("Delete")
        self.btn_del_profile.setObjectName("DeleteBtn")
        profile_btns.addWidget(self.btn_add_profile)
        profile_btns.addWidget(self.btn_del_profile)
        
        self.left_col.addWidget(self.profile_input)
        self.left_col.addLayout(profile_btns)

        # Right: Plugins
        self.right_col = QVBoxLayout()
        version_label = QLabel(f"3DS MAX {max_version} PLUGINS")
        version_label.setStyleSheet("color: #007acc; font-weight: bold; font-size: 14px;")
        self.right_col.addWidget(version_label)
        
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search plugins (e.g. tyFlow, Octane)...")
        self.right_col.addWidget(self.search_input)

        filter_layout = QHBoxLayout()
        self.show_all_cb = QCheckBox("Show System Files (Advanced)")
        self.show_all_cb.setStyleSheet("color: #888; font-size: 11px;")
        filter_layout.addWidget(self.show_all_cb)
        filter_layout.addStretch()
        self.right_col.addLayout(filter_layout)
        
        self.plugin_list = QListWidget()
        self.right_col.addWidget(self.plugin_list)

        self.btn_save = QPushButton("Save Configuration")
        self.btn_save.setObjectName("SaveBtn")
        self.btn_launch = QPushButton("APPLY && CLOSE")
        self.btn_launch.setObjectName("ApplyBtn")
        
        self.right_col.addWidget(self.btn_save)
        self.right_col.addWidget(self.btn_launch)

        self.layout.addLayout(self.left_col, 1)
        self.layout.addLayout(self.right_col, 2)