import sys
import os
import socket
import subprocess
import requests
import webbrowser
import threading
from datetime import datetime
from time import sleep
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QListWidget, QTextEdit, QHBoxLayout, QLineEdit, QTabWidget

# Program: JadivDevControl for C14, verzia 7

def check_for_updates(log_widget):
    update_url = 'https://github.com/jan-tdy/aplikacia8ejw8idue8wo/raw/main/main.py'
    target_path = '/home/dpv/j44softapps-socketcontrol/main.py'
    while True:
        try:
            response = requests.get(update_url)
            if response.status_code == 200:
                with open(target_path, 'rb') as f:
                    local_content = f.read()
                if response.content != local_content:
                    log_widget.append("Nová verzia aplikácie je dostupná na Githube!")
            sleep(900)
        except requests.RequestException as e:
            log_widget.append(f"Chyba pri kontrole aktualizácie: {e}")

class ControlApp(QWidget):
    def __init__(self, devices):
        super().__init__()
        self.devices = devices
        self.init_ui()
        self.start_update_checker()

    def init_ui(self):
        layout = QVBoxLayout()
        self.tabs = QTabWidget()

        self.tab_wol = QWidget()
        self.init_wol_ui()
        self.tabs.addTab(self.tab_wol, "Wake-on-LAN")

        self.tab_zasuvky = QWidget()
        self.init_zasuvky_ui()
        self.tabs.addTab(self.tab_zasuvky, "Zásuvky")
        
        self.tab_strecha = QWidget()
        self.init_strecha_ui()
        self.tabs.addTab(self.tab_strecha, "Strecha")

        self.tab_logy = QWidget()
        self.init_log_ui()
        self.tabs.addTab(self.tab_logy, "Logy")

        layout.addWidget(self.tabs)
        self.setLayout(layout)
        self.setWindowTitle("JadivDevControl for C14, verzia 7")
        self.resize(800, 600)

    def start_update_checker(self):
        self.log_widget = QTextEdit()
        threading.Thread(target=check_for_updates, args=(self.log_widget,), daemon=True).start()

    def init_log_ui(self):
        layout = QVBoxLayout()
        self.log_widget = QTextEdit()
        self.log_widget.setReadOnly(True)
        layout.addWidget(self.log_widget)
        self.tab_logy.setLayout(layout)
    
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
        self.tab_wol.setLayout(layout)
    
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
        slot_names = {1: "none(1)", 2: "AZ2000(2)", 3: "C14(3)", 4: "UNKNOWN(4)"}
        for slot in range(1, 5):
            zasuvka_layout = QHBoxLayout()
            stav_label = QLabel("OFF")
            btn_on = QPushButton(f"Zapnúť {slot_names[slot]}")
            btn_off = QPushButton(f"Vypnúť {slot_names[slot]}")
            btn_on.clicked.connect(lambda checked, slot=slot: self.zapni_zasuvku(slot))
            btn_off.clicked.connect(lambda checked, slot=slot: self.vypni_zasuvku(slot))
            zasuvka_layout.addWidget(stav_label)
            zasuvka_layout.addWidget(btn_on)
            zasuvka_layout.addWidget(btn_off)
            layout.addLayout(zasuvka_layout)
        self.tab_zasuvky.setLayout(layout)

    def zapni_zasuvku(self, slot):
        subprocess.run(["syspmctl", "-o", str(slot)], shell=True)

    def vypni_zasuvku(self, slot):
        subprocess.run(["syspmctl", "-f", str(slot)], shell=True)

    def init_strecha_ui(self):
        layout = QVBoxLayout()
        btn_strecha_on = QPushButton("Pohnut strechou")
        btn_strecha_on.clicked.connect(self.run_strecha_on)
        layout.addWidget(btn_strecha_on)
        self.tab_strecha.setLayout(layout)

    def run_strecha_on(self):
        subprocess.run(["bash", "-c", "cd /home/dpv/Downloads/usb-relay-hid-master/commandline/makemake && ./strecha_on.sh"], shell=True)
    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    devices = [
        {'name': 'hlavny', 'mac': 'e0:d5:5e:df:c6:4e', 'ip': '172.20.20.133'},
        {'name': 'VNT', 'mac': '78:24:af:9c:06:e7', 'ip': '172.20.20.123'},
        {'name': 'C14', 'mac': 'e0:d5:5e:37:4f:ad', 'ip': '172.20.20.103'},
        {'name': 'AZ2000 mount', 'mac': '00:c0:08:a9:c2:32', 'ip': '172.20.20.10'},
        {'name': 'GM3000 mount', 'mac': '00:c0:08:aa:35:12', 'ip': '172.20.20.12'}
    ]
    window = ControlApp(devices)
    window.show()
    sys.exit(app.exec_())
