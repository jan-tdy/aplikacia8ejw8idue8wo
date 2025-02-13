import sys
import os
import subprocess
import requests
from datetime import datetime
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QListWidget, QTextEdit, QHBoxLayout, QLineEdit

# Program: JadivDevControl for C14, verzia 7.3

def log_message(log_widget, message):
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    log_widget.append(f"{timestamp} {message}")

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
            log_message(log_widget, "Aktualizácia úspešne stiahnutá. Zatvorte a znovu otvorte program.")
        else:
            log_message(log_widget, "Chyba pri sťahovaní aktualizácie.")
    except requests.RequestException as e:
        log_message(log_widget, f"Chyba pri sťahovaní aktualizácie: {e}")

class ControlApp(QWidget):
    def __init__(self, devices):
        super().__init__()
        self.devices = devices
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.intro_label = QLabel("JadivDevControl for C14, verzia 7.3")
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
        self.init_terminal_ui(layout)

        self.setLayout(layout)
        self.setWindowTitle("JadivDevControl for C14, verzia 7.3")
        self.resize(800, 600)

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
            try:
                subprocess.run(["wakeonlan", mac_address], shell=True, check=True)
                log_message(self.log_widget, f"Odoslaný WOL pre {mac_address}")
            except subprocess.CalledProcessError as e:
                log_message(self.log_widget, f"Chyba pri WOL: {e}")
        else:
            log_message(self.log_widget, "Nezadaná MAC adresa!")

    def init_zasuvky_ui(self, layout):
        slot_names = {1: "none(1)", 2: "AZ2000(2)", 3: "C14(3)", 4: "UNKNOWN(4)"}
        self.slot_labels = {}

        for slot in range(1, 5):
            zasuvka_layout = QHBoxLayout()
            stav_label = QLabel("OFF")
            self.slot_labels[slot] = stav_label
            btn_on = QPushButton(f"Zapnúť {slot_names[slot]}")
            btn_off = QPushButton(f"Vypnúť {slot_names[slot]}")
            btn_on.clicked.connect(lambda checked, s=slot: self.zapni_zasuvku(s))
            btn_off.clicked.connect(lambda checked, s=slot: self.vypni_zasuvku(s))
            zasuvka_layout.addWidget(stav_label)
            zasuvka_layout.addWidget(btn_on)
            zasuvka_layout.addWidget(btn_off)
            layout.addLayout(zasuvka_layout)

    def zapni_zasuvku(self, slot):
        try:
            subprocess.run(["syspmctl", "-o", str(slot)], shell=True, check=True)
            self.slot_labels[slot].setText("ON")
            log_message(self.log_widget, f"Zásuvka {slot} zapnutá.")
        except subprocess.CalledProcessError as e:
            log_message(self.log_widget, f"Chyba pri zapínaní zásuvky {slot}: {e}")

    def vypni_zasuvku(self, slot):
        try:
            subprocess.run(["syspmctl", "-f", str(slot)], shell=True, check=True)
            self.slot_labels[slot].setText("OFF")
            log_message(self.log_widget, f"Zásuvka {slot} vypnutá.")
        except subprocess.CalledProcessError as e:
            log_message(self.log_widget, f"Chyba pri vypínaní zásuvky {slot}: {e}")

    def init_strecha_ui(self, layout):
        btn_strecha_on = QPushButton("Pohnut strechou")
        btn_strecha_on.clicked.connect(self.run_strecha_on)
        layout.addWidget(btn_strecha_on)

    def run_strecha_on(self):
        try:
            subprocess.run("cd /home/dpv/Downloads/usb-relay-hid-master/commandline/makemake && ./strecha_on.sh", shell=True, check=True)
            log_message(self.log_widget, "Strecha pohybovaná.")
        except subprocess.CalledProcessError as e:
            log_message(self.log_widget, f"Chyba pri pohybe strechy: {e}")

    def init_terminal_ui(self, layout):
        self.terminal_input = QLineEdit()
        self.terminal_input.setPlaceholderText("Zadajte príkaz...")
        self.terminal_input.returnPressed.connect(self.execute_command)
        layout.addWidget(self.terminal_input)

    def execute_command(self):
        command = self.terminal_input.text().strip()
        log_message(self.log_widget, f"Spustený príkaz: {command}")

        if command == "update":
            manual_update(self.log_widget)
        elif command.startswith("zasuvka"):
            _, action, slot = command.split()
            slot = int(slot)
            if action == "on":
                self.zapni_zasuvku(slot)
            elif action == "off":
                self.vypni_zasuvku(slot)
        elif command.startswith("wol"):
            _, mac = command.split()
            subprocess.run(["wakeonlan", mac], shell=True, check=True)
            log_message(self.log_widget, f"Odoslaný WOL pre {mac}")
        elif command == "strecha":
            self.run_strecha_on()
        else:
            log_message(self.log_widget, "Neznámy príkaz!")

        self.terminal_input.clear()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    devices = []
    window = ControlApp(devices)
    window.show()
    sys.exit(app.exec_())