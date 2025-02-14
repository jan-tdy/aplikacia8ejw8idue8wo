import sys
import os
import subprocess
import requests
from datetime import datetime
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QListWidget, QTextEdit, QHBoxLayout, QLineEdit

# Program: JadivDevControl for C14, verzia 7.3

def log_message(log_widget, message):
    """Zapisuje sprÃ¡vy do log widgetu a konzoly."""
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    log_widget.append(f"{timestamp} {message}")
    print(f"{timestamp} {message}")

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

        self.init_wol_ui(layout)
        self.init_zasuvky_ui(layout)
        self.init_strecha_ui(layout)

        self.setLayout(layout)
        self.setWindowTitle("JadivDevControl for C14, verzia 7.3")
        self.resize(800, 600)

    def init_wol_ui(self, layout):
        """InicializÃ¡cia sekcie Wake-on-LAN."""
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
        """Odoslanie WOL signÃ¡lu."""
        selected = self.list_widget.currentRow()
        mac_address = self.mac_input.text().strip()
        if selected >= 0:
            device = self.devices[selected]
            mac_address = device['mac']
        if mac_address:
            try:
                subprocess.run(f"wakeonlan {mac_address}", shell=True, check=True)
                log_message(self.log_widget, f"OdoslanÃ½ WOL pre {mac_address}")
            except subprocess.CalledProcessError as e:
                log_message(self.log_widget, f"Chyba pri WOL: {e}")
        else:
            log_message(self.log_widget, "NezadanÃ¡ MAC adresa!")

    def init_zasuvky_ui(self, layout):
        """InicializÃ¡cia sekcie zÃ¡suviek."""
        slot_names = {1: "none(1)", 2: "AZ2000(2)", 3: "C14(3)", 4: "UNKNOWN(4)"}
        self.slot_labels = {}

        for slot in range(1, 5):
            zasuvka_layout = QHBoxLayout()
            stav_label = QLabel("OFF")
            self.slot_labels[slot] = stav_label

            btn_on = QPushButton(f"ZapnÃºÅ¥ {slot_names[slot]}")
            btn_off = QPushButton(f"VypnÃºÅ¥ {slot_names[slot]}")

            btn_on.clicked.connect(lambda checked, s=slot: self.zapni_zasuvku(s))
            btn_off.clicked.connect(lambda checked, s=slot: self.vypni_zasuvku(s))

            zasuvka_layout.addWidget(stav_label)
            zasuvka_layout.addWidget(btn_on)
            zasuvka_layout.addWidget(btn_off)
            layout.addLayout(zasuvka_layout)

    def zapni_zasuvku(self, slot):
        """Zapnutie zÃ¡suvky cez syspmctl."""
        try:
            command = f"sispmctl -o {slot}"
            subprocess.run(command, shell=True, check=True)
            self.slot_labels[slot].setText("ON")
            log_message(self.log_widget, f"ZÃ¡suvka {slot} zapnutÃ¡. PrÃ­kaz: {command}")
        except subprocess.CalledProcessError as e:
            log_message(self.log_widget, f"Chyba pri zapÃ­nanÃ­ zÃ¡suvky {slot}: {e}")

    def vypni_zasuvku(self, slot):
        """Vypnutie zÃ¡suvky cez syspmctl."""
        try:
            command = f"sispmctl -f {slot}"
            subprocess.run(command, shell=True, check=True)
            self.slot_labels[slot].setText("OFF")
            log_message(self.log_widget, f"ZÃ¡suvka {slot} vypnutÃ¡. PrÃ­kaz: {command}")
        except subprocess.CalledProcessError as e:
            log_message(self.log_widget, f"Chyba pri vypÃ­nanÃ­ zÃ¡suvky {slot}: {e}")

    def init_strecha_ui(self, layout):
        """InicializÃ¡cia sekcie strechy."""
        btn_strecha_on = QPushButton("Pohnut strechou")
        btn_strecha_on.clicked.connect(self.run_strecha_on)
        layout.addWidget(btn_strecha_on)

    def run_strecha_on(self):
        """OvlÃ¡danie strechy cez shell skript."""
        try:
            command = "cd /home/dpv/Downloads/usb-relay-hid-master/commandline/makemake && ./strecha_on.sh"
            subprocess.run(command, shell=True, check=True)
            log_message(self.log_widget, "Strecha pohybovanÃ¡.")
        except subprocess.CalledProcessError as e:
            log_message(self.log_widget, f"Chyba pri pohybe strechy: {e}")

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
