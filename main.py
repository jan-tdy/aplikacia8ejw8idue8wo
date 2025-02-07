import sys
import os
import socket
import subprocess
import requests
import webbrowser
import threading
import paramiko
from datetime import datetime
from time import sleep
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QListWidget, QTextEdit, QHBoxLayout, QLineEdit

# Program: JadivDevControl for C14, verzia 7.4

WINCONFIG_PATH = "/home/dpv/j44softapps-socketcontrol/winconfig.txt"

def load_winconfig():
    config = {}
    if os.path.exists(WINCONFIG_PATH):
        with open(WINCONFIG_PATH, 'r') as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) == 3 and parts[0] == "ip":
                    config['ip'] = parts[1]
                elif len(parts) == 3 and parts[0] == "psw":
                    config['password'] = parts[1]
                elif len(parts) == 3:
                    config[parts[0]] = parts[1]
    return config

def send_ssh_command(command, log_widget):
    config = load_winconfig()
    if 'ip' not in config or 'password' not in config:
        log_widget.append("Chyba: IP adresa alebo heslo nie sú definované v konfiguračnom súbore.")
        return
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(config['ip'], username='admin', password=config['password'])
        stdin, stdout, stderr = ssh.exec_command(command)
        output = stdout.read().decode()
        error = stderr.read().decode()
        if output:
            log_widget.append(f"Výstup: {output}")
        if error:
            log_widget.append(f"Chyba: {error}")
        ssh.close()
    except Exception as e:
        log_widget.append(f"Chyba pri odosielaní SSH príkazu: {e}")

class ControlApp(QWidget):
    def __init__(self, devices):
        super().__init__()
        self.devices = devices
        self.init_ui()
        self.start_update_checker()

    def init_ui(self):
        layout = QVBoxLayout()
        self.intro_label = QLabel("JadivDevControl for C14, verzia 7.4")
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
        self.init_astrofoto_ui(layout)

        self.setLayout(layout)
        self.setWindowTitle("JadivDevControl for C14, verzia 7.4")
        self.resize(800, 600)

    def init_astrofoto_ui(self, layout):
        layout.addWidget(QLabel("Astrofoto - Ovládanie Windows počítača"))
        config = load_winconfig()

        for key, command in config.items():
            if key not in ["ip", "password"]:
                button = QPushButton(key.replace("_", " "))
                button.clicked.connect(lambda checked, cmd=command: send_ssh_command(cmd, self.log_widget))
                layout.addWidget(button)

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
