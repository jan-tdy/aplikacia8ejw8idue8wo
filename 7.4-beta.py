import sys
import os
import subprocess
import requests
import json
from datetime import datetime
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QListWidget, QTextEdit, QHBoxLayout, QLineEdit, QTabWidget, QStackedWidget, QComboBox
from PyQt5.QtGui import QPalette, QColor

# Súbor pre uloženie nastavení
SETTINGS_FILE = "settings.json"
MAC_FILE = "mac.json"

def load_settings():
    """Načíta nastavenia zo súboru settings.json."""
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r") as f:
            return json.load(f)
    return {"theme": "dark", "view_mode": "tabs"}

def save_settings(settings):
    """Uloží nastavenia do súboru settings.json."""
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=4)

def save_mac_addresses(devices):
    """Uloží MAC adresy do súboru mac.json."""
    with open(MAC_FILE, "w") as f:
        json.dump(devices, f, indent=4)

# Načítanie nastavení pri spustení
settings = load_settings()

def log_message(log_widget, message):
    """Zapisuje správy do log widgetu a konzoly."""
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    log_widget.append(f"{timestamp} {message}")
    print(f"{timestamp} {message}")

class ControlApp(QWidget):
    def __init__(self, devices):
        super().__init__()
        self.devices = devices
        self.settings = load_settings()
        self.init_ui()
        save_mac_addresses(devices)

    def init_ui(self):
        layout = QVBoxLayout()

        # Nastavenie farby podľa nastavení
        self.apply_theme(self.settings["theme"])

        self.intro_label = QLabel("JadivDevControl for C14, verzia 7.4")
        layout.addWidget(self.intro_label)

        # Výber zobrazenia (karty alebo menu)
        if self.settings["view_mode"] == "tabs":
            self.tabs = QTabWidget()
            self.page_wol = QWidget()
            self.page_zasuvky = QWidget()
            self.page_strecha = QWidget()
            self.page_log = QWidget()
            self.page_settings = QWidget()

            self.tabs.addTab(self.page_wol, "WOL")
            self.tabs.addTab(self.page_zasuvky, "Zásuvky")
            self.tabs.addTab(self.page_strecha, "Strecha")
            self.tabs.addTab(self.page_log, "Log")
            self.tabs.addTab(self.page_settings, "Nastavenia")

            layout.addWidget(self.tabs)
        else:
            self.stack = QStackedWidget()
            self.page_wol = QWidget()
            self.page_zasuvky = QWidget()
            self.page_strecha = QWidget()
            self.page_log = QWidget()
            self.page_settings = QWidget()

            self.stack.addWidget(self.page_wol)
            self.stack.addWidget(self.page_zasuvky)
            self.stack.addWidget(self.page_strecha)
            self.stack.addWidget(self.page_log)
            self.stack.addWidget(self.page_settings)

            menu_layout = QHBoxLayout()
            self.btn_wol = QPushButton("WOL")
            self.btn_zasuvky = QPushButton("Zásuvky")
            self.btn_strecha = QPushButton("Strecha")
            self.btn_log = QPushButton("Log")
            self.btn_settings = QPushButton("Nastavenia")
            self.btn_move_and_download = QPushButton("Move and Download Files")

            self.btn_wol.clicked.connect(lambda: self.stack.setCurrentIndex(0))
            self.btn_zasuvky.clicked.connect(lambda: self.stack.setCurrentIndex(1))
            self.btn_strecha.clicked.connect(lambda: self.stack.setCurrentIndex(2))
            self.btn_log.clicked.connect(lambda: self.stack.setCurrentIndex(3))
            self.btn_settings.clicked.connect(lambda: self.stack.setCurrentIndex(4))
            self.btn_move_and_download.clicked.connect(self.move_and_download_files)

            menu_layout.addWidget(self.btn_wol)
            menu_layout.addWidget(self.btn_zasuvky)
            menu_layout.addWidget(self.btn_strecha)
            menu_layout.addWidget(self.btn_log)
            menu_layout.addWidget(self.btn_settings)
            menu_layout.addWidget(self.btn_move_and_download)

            layout.addLayout(menu_layout)
            layout.addWidget(self.stack)

        self.init_wol_ui()
        self.init_zasuvky_ui()
        self.init_strecha_ui()
        self.init_log_ui()
        self.init_settings_ui()

        self.setLayout(layout)
        self.setWindowTitle("JadivDevControl for C14, verzia 7.4")
        self.resize(800, 600)

    def apply_theme(self, theme):
        """Nastaví tmavý alebo svetlý režim."""
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
        self.list_widget = QListWidget()
        for device in self.devices:
            self.list_widget.addItem(f"{device['name']} - {device['mac']} - {device['ip']}")
        layout.addWidget(self.list_widget)
        self.mac_input = QLineEdit()
        self.mac_input.setPlaceholderText("Zadajte MAC adresu pre WOL")
        layout.addWidget(self.mac_input)
        self.btn_wake = QPushButton("Wake")
        self.btn_wake.clicked.connect(self.wake_device)
        layout.addWidget(self.btn_wake)
        self.page_wol.setLayout(layout)

    def wake_device(self):
        selected = self.list_widget.currentRow()
        mac_address = self.mac_input.text().strip()
        if selected >= 0:
            device = self.devices[selected]
            mac_address = device['mac']
        if mac_address:
            subprocess.run(["wakeonlan", mac_address], shell=True)
        else:
            print("Nezadaná MAC adresa!")

    def init_zasuvky_ui(self):
        layout = QVBoxLayout()
        self.btn_on = QPushButton("Zapnúť zásuvku")
        self.btn_off = QPushButton("Vypnúť zásuvku")
        self.btn_on.clicked.connect(lambda: subprocess.run(["sispmctl", "-o", "1"], shell=True))
        self.btn_off.clicked.connect(lambda: subprocess.run(["sispmctl", "-f", "1"], shell=True))
        layout.addWidget(self.btn_on)
        layout.addWidget(self.btn_off)
        self.page_zasuvky.setLayout(layout)

    def init_strecha_ui(self):
        layout = QVBoxLayout()
        self.btn_strecha_on = QPushButton("Pohnut strechou")
        self.btn_strecha_on.clicked.connect(lambda: subprocess.run("cd /home/dpv/Downloads/usb-relay-hid-master/commandline/makemake && ./strecha_on.sh", shell=True))
        layout.addWidget(self.btn_strecha_on)
        self.page_strecha.setLayout(layout)

    def init_log_ui(self):
        layout = QVBoxLayout()
        self.log_widget = QTextEdit()
        self.log_widget.setReadOnly(True)
        layout.addWidget(self.log_widget)
        self.page_log.setLayout(layout)

    def move_and_download_files(self):
        # Move files from /home/dpv/j44softapps-socketcontrol/ to /home/dpv/j44softapps-socketcontrol/old1
        os.makedirs("/home/dpv/j44softapps-socketcontrol/old1", exist_ok=True)
        for filename in os.listdir("/home/dpv/j44softapps-socketcontrol/"):
            if filename != "old1":
                os.rename(f"/home/dpv/j44softapps-socketcontrol/{filename}", f"/home/dpv/j44softapps-socketcontrol/old1/{filename}")

        # Clone the repository to /home/dpv/j44softapps-socketcontrol/
        subprocess.run("git clone https://github.com/jan-tdy/aplikacia8ejw8idue8wo /home/dpv/j44softapps-socketcontrol/", shell=True)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    devices = [
        {'name': 'hlavny', 'mac': 'e0:d5:5e:df:c6:4e', 'ip': '172.20.20.133'},
        {'name': 'VNT', 'mac': '78:24:af:9c:06:e7', 'ip': '172.20.20.123'}
    ]
    window = ControlApp(devices)
    window.show()
    sys.exit(app.exec_())
