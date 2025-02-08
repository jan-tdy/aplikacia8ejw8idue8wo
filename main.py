import sys
import os
import socket
import subprocess
import requests
import webbrowser
import threading
from datetime import datetime
from time import sleep
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QListWidget, QTextEdit, QHBoxLayout, QLineEdit

# Program: JadivDevControl for C14, verzia 7.2

def check_for_updates(log_widget):
    update_url = 'https://github.com/jan-tdy/aplikacia8ejw8idue8wo/raw/main/main.py'
    try:
        response = requests.get(update_url)
        if response.status_code == 200:
            log_widget.append("Nová verzia aplikácie je dostupná na Githube!")
        else:
            log_widget.append("Chyba pri kontrole aktualizácie.")
    except requests.RequestException as e:
        log_widget.append(f"Chyba pri kontrole aktualizácie: {e}")

def manual_update(log_widget):
    update_url = 'https://github.com/jan-tdy/aplikacia8ejw8idue8wo/raw/main/main.py'
    target_path = '/home/dpv/j44softapps-socketcontrol/main.py'
    try:
        response = requests.get(update_url)
        if response.status_code == 200:
            if os.path.exists(target_path):
                os.remove(target_path)
            with open(target_path, 'wb') as f:
                f.write(response.content)
            log_widget.append("Aktualizácia úspešne stiahnutá. Zatvorte a znovu otvorte program.")
        else:
            log_widget.append("Chyba pri sťahovaní aktualizácie.")
    except requests.RequestException as e:
        log_widget.append(f"Chyba pri sťahovaní aktualizácie: {e}")

class ControlApp(QWidget):
    def __init__(self, devices):
        super().__init__()
        self.devices = devices
        self.init_ui()
        self.start_update_checker()

    def init_ui(self):
        layout = QVBoxLayout()
        self.intro_label = QLabel("JadivDevControl for C14, verzia 7.2")
        layout.addWidget(self.intro_label)

        self.log_widget = QTextEdit()
        self.log_widget.setReadOnly(True)
        layout.addWidget(self.log_widget)

        self.ota_button = QPushButton("OTA Update")
        self.ota_button.clicked.connect(lambda: manual_update(self.log_widget))
        layout.addWidget(self.ota_button)

        self.init_wol_ui(layout)
        self.init_zasuvky_ui(layout)
        self.init_strecha_ui(layout)

        self.setLayout(layout)
        self.setWindowTitle("JadivDevControl for C14, verzia 7.2")
        self.resize(800, 600)

    def start_update_checker(self):
        threading.Thread(target=self.check_for_updates_periodically, daemon=True).start()

    def check_for_updates_periodically(self):
        while True:
            check_for_updates(self.log_widget)
            sleep(3600)

    def init_wol_ui(self, layout):
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
    
    def init_zasuvky_ui(self, layout):
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

    def zapni_zasuvku(self, slot):
        subprocess.run(["syspmctl", "-o", str(slot)], shell=True)

    def vypni_zasuvku(self, slot):
        subprocess.run(["syspmctl", "-f", str(slot)], shell=True)

    def init_strecha_ui(self, layout):
        btn_strecha_on = QPushButton("Pohnut strechou")
        btn_strecha_on.clicked.connect(self.run_strecha_on)
        layout.addWidget(btn_strecha_on)

    def run_strecha_on(self):
        subprocess.run(["cd /home/dpv/Downloads/usb-relay-hid-master/commandline/makemake && ./strecha_on.sh"], shell=True)
    
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
