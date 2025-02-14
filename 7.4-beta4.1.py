import sys
import os
import subprocess
import requests
import json
from datetime import datetime
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QListWidget, QTextEdit, QHBoxLayout, QLineEdit, QStackedWidget, QComboBox
from PyQt5.QtGui import QPalette, QColor

# Nastavenia
SETTINGS_FILE = "settings.json"
MAC_FILE = "mac.json"

# Načítanie a uloženie nastavení
def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r") as f:
            return json.load(f)
    return {"theme": "light", "view_mode": "sections"}  # Predvolená téma je teraz svetlá, prepnuté na sekcie

def save_settings(settings):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=4)

def log_message(log_widget, message):
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    log_widget.append(f"{timestamp} {message}")
    print(f"{timestamp} {message}")

class ControlApp(QWidget):
    def __init__(self, devices):
        super().__init__()
        self.devices = devices
        self.settings = load_settings()
        self.init_ui()
        
    def apply_theme(self, theme):
        palette = self.palette()
        if theme == "dark":
            palette.setColor(QPalette.Window, QColor(30, 30, 30))
            palette.setColor(QPalette.WindowText, QColor(255, 255, 255))
        else:
            palette.setColor(QPalette.Window, QColor(240, 240, 240))
            palette.setColor(QPalette.WindowText, QColor(0, 0, 0))
        self.setPalette(palette)

    def init_ui(self):
        layout = QVBoxLayout()
        self.apply_theme(self.settings["theme"])
        
        self.intro_label = QLabel("JadivDevControl for C14, verzia 7.4")
        layout.addWidget(self.intro_label)
        
        self.stack = QStackedWidget()
        self.page_wol = QWidget()
        self.page_zasuvky = QWidget()
        self.page_strecha = QWidget()
        self.page_log = QWidget()
        self.page_settings = QWidget()
        self.page_ota = QWidget()
        
        self.stack.addWidget(self.page_wol)
        self.stack.addWidget(self.page_zasuvky)
        self.stack.addWidget(self.page_strecha)
        self.stack.addWidget(self.page_log)
        self.stack.addWidget(self.page_settings)
        self.stack.addWidget(self.page_ota)
        
        menu_layout = QHBoxLayout()
        self.btn_wol = QPushButton("WOL")
        self.btn_zasuvky = QPushButton("Zásuvky")
        self.btn_strecha = QPushButton("Strecha")
        self.btn_log = QPushButton("Log")
        self.btn_settings = QPushButton("Nastavenia")
        self.btn_ota = QPushButton("OTA Update")

        self.btn_wol.clicked.connect(lambda: self.stack.setCurrentWidget(self.page_wol))
        self.btn_zasuvky.clicked.connect(lambda: self.stack.setCurrentWidget(self.page_zasuvky))
        self.btn_strecha.clicked.connect(lambda: self.stack.setCurrentWidget(self.page_strecha))
        self.btn_log.clicked.connect(lambda: self.stack.setCurrentWidget(self.page_log))
        self.btn_settings.clicked.connect(lambda: self.stack.setCurrentWidget(self.page_settings))
        self.btn_ota.clicked.connect(lambda: self.stack.setCurrentWidget(self.page_ota))

        menu_layout.addWidget(self.btn_wol)
        menu_layout.addWidget(self.btn_zasuvky)
        menu_layout.addWidget(self.btn_strecha)
        menu_layout.addWidget(self.btn_log)
        menu_layout.addWidget(self.btn_settings)
        menu_layout.addWidget(self.btn_ota)

        layout.addLayout(menu_layout)
        layout.addWidget(self.stack)
        self.init_wol_ui()
        self.init_zasuvky_ui()
        self.init_strecha_ui()
        self.init_log_ui()
        self.init_settings_ui()
        self.init_ota_ui()
        
        self.setLayout(layout)
        self.setWindowTitle("JadivDevControl for C14, verzia 7.4")
        self.resize(800, 600)
        self.show()
    
    def init_wol_ui(self):
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Wake-on-LAN (WOL)"))
        self.page_wol.setLayout(layout)
    
    def init_strecha_ui(self):
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Ovládanie strechy"))
        self.page_strecha.setLayout(layout)
    
    def init_log_ui(self):
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Systémový log"))
        self.page_log.setLayout(layout)
    
    def init_settings_ui(self):
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Nastavenia systému"))
        self.page_settings.setLayout(layout)
    
    def init_ota_ui(self):
        layout = QVBoxLayout()
        layout.addWidget(QLabel("OTA Update - Aktualizácia systému"))
        self.page_ota.setLayout(layout)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    devices = [
        {'name': 'VNT', 'mac': '78:24:af:9c:06:e7', 'ip': '172.20.20.123'},
        {'name': 'C14', 'mac': 'e0:d5:5e:37:4f:ad', 'ip': '172.20.20.103'},
        {'name': 'AZ2000 mount', 'mac': '00:c0:08:a9:c2:32', 'ip': '172.20.20.10'},
        {'name': 'AZ2000 RPi allsky', 'mac': 'd8:3a:dd:9a:05:d4', 'ip': '172.20.20.116'},
        {'name': 'GM3000 mount', 'mac': '00:c0:08:aa:35:12', 'ip': '172.20.20.12'},
        {'name': 'GM3000 RPi pi1', 'mac': 'd8:3a:dd:89:4d:d0', 'ip': '172.20.20.112'}
    ]
    app.setStyle("Fusion")
    window = ControlApp(devices)
    window.show()
    sys.exit(app.exec_())
