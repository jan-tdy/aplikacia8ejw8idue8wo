import sys
import os
import subprocess
import requests
import json
from datetime import datetime
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QListWidget, QTextEdit, QHBoxLayout, QLineEdit, QTabWidget, QStackedWidget, QComboBox
from PyQt5.QtGui import QPalette, QColor

# Nastavenia
SETTINGS_FILE = "settings.json"
MAC_FILE = "mac.json"

# Načítanie a uloženie nastavení
def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r") as f:
            return json.load(f)
    return {"theme": "dark", "view_mode": "tabs"}

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

    def init_ui(self):
        layout = QVBoxLayout()
        self.apply_theme(self.settings["theme"])
        
        self.intro_label = QLabel("JadivDevControl for C14, verzia 7.4")
        layout.addWidget(self.intro_label)
        
        self.tabs = QTabWidget()
        self.page_wol = QWidget()
        self.page_zasuvky = QWidget()
        self.page_strecha = QWidget()
        self.page_log = QWidget()
        self.page_settings = QWidget()
        self.page_ota = QWidget()
        
        self.tabs.addTab(self.page_wol, "WOL")
        self.tabs.addTab(self.page_zasuvky, "Zásuvky")
        self.tabs.addTab(self.page_strecha, "Strecha")
        self.tabs.addTab(self.page_log, "Log")
        self.tabs.addTab(self.page_settings, "Nastavenia")
        self.tabs.addTab(self.page_ota, "OTA Update")
        
        layout.addWidget(self.tabs)
        self.init_wol_ui()
        self.init_zasuvky_ui()
        self.init_strecha_ui()
        self.init_log_ui()
        self.init_settings_ui()
        self.init_ota_ui()
        
        self.setLayout(layout)
        self.setWindowTitle("JadivDevControl for C14, verzia 7.4")
        self.resize(800, 600)

    def apply_theme(self, theme):
        palette = self.palette()
        if theme == "dark":
            palette.setColor(QPalette.Window, QColor(30, 30, 30))
            palette.setColor(QPalette.WindowText, QColor(255, 255, 255))
        else:
            palette.setColor(QPalette.Window, QColor(240, 240, 240))
            palette.setColor(QPalette.WindowText, QColor(0, 0, 0))
        self.setPalette(palette)

    def init_wol_ui(self):
        layout = QVBoxLayout()
        self.page_wol.setLayout(layout)
    
    def init_zasuvky_ui(self):
        layout = QVBoxLayout()
        slot_names = {1: "none(1)", 2: "AZ2000(2)", 3: "C14(3)", 4: "UNKNOWN(4)"}
        self.slot_labels = {}
        for slot in range(1, 5):
            slot_layout = QHBoxLayout()
            label = QLabel("OFF")
            self.slot_labels[slot] = label
            btn_on = QPushButton(f"Zapnúť {slot_names[slot]}")
            btn_off = QPushButton(f"Vypnúť {slot_names[slot]}")
            btn_on.clicked.connect(lambda checked, s=slot: self.toggle_zasuvka(s, True))
            btn_off.clicked.connect(lambda checked, s=slot: self.toggle_zasuvka(s, False))
            slot_layout.addWidget(label)
            slot_layout.addWidget(btn_on)
            slot_layout.addWidget(btn_off)
            layout.addLayout(slot_layout)
        self.page_zasuvky.setLayout(layout)

    def toggle_zasuvka(self, slot, turn_on):
        action = "-o" if turn_on else "-f"
        subprocess.run(f"sispmctl {action} {slot}", shell=True)
        self.slot_labels[slot].setText("ON" if turn_on else "OFF")

    def init_strecha_ui(self):
        layout = QVBoxLayout()
        btn_strecha_on = QPushButton("Pohnut strechou")
        btn_strecha_on.clicked.connect(lambda: subprocess.run("cd /home/dpv/Downloads/usb-relay-hid-master/commandline/makemake && ./strecha_on.sh", shell=True))
        layout.addWidget(btn_strecha_on)
        self.page_strecha.setLayout(layout)
    
    def init_log_ui(self):
        layout = QVBoxLayout()
        self.log_widget = QTextEdit()
        self.log_widget.setReadOnly(True)
        layout.addWidget(self.log_widget)
        self.page_log.setLayout(layout)
    
    def init_ota_ui(self):
        layout = QVBoxLayout()
        btn_update = QPushButton("OTA Update")
        btn_update.clicked.connect(self.ota_update)
        layout.addWidget(btn_update)
        self.page_ota.setLayout(layout)
    
    def ota_update(self):
        subprocess.run("git pull", shell=True)
        log_message(self.log_widget, "Systém bol aktualizovaný cez OTA Update.")

if __name__ == "__main__":
    devices = [
        {'name': 'VNT', 'mac': '78:24:af:9c:06:e7', 'ip': '172.20.20.123'},
        {'name': 'C14', 'mac': 'e0:d5:5e:37:4f:ad', 'ip': '172.20.20.103'},
        {'name': 'AZ2000 mount', 'mac': '00:c0:08:a9:c2:32', 'ip': '172.20.20.10'},
        {'name': 'AZ2000 RPi allsky', 'mac': 'd8:3a:dd:9a:05:d4', 'ip': '172.20.20.116'},
        {'name': 'GM3000 mount', 'mac': '00:c0:08:aa:35:12', 'ip': '172.20.20.12'},
        {'name': 'GM3000 RPi pi1', 'mac': 'd8:3a:dd:89:4d:d0', 'ip': '172.20.20.112'}
    ]
    app = QApplication(sys.argv)
    window = ControlApp(devices)
    window.show()
    sys.exit(app.exec_())
