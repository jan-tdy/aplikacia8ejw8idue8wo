import sys
import os
import socket
import subprocess
import requests
from datetime import datetime
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QListWidget, QTextEdit, QHBoxLayout, QLineEdit
from PyQt5.QtWebEngineWidgets import QWebEngineView

# Program: JadivDevControl for C14, verzia 5-2-2025_05

# --------------------------
# Funkcia pre Wake-on-LAN
def send_wol(mac_address, log_widget):
    mac_address = mac_address.replace(':', '').replace('-', '')
    if len(mac_address) != 12:
        log_widget.append("Chyba: Neplatná MAC adresa.")
        return False
    try:
        data = b'\xff' * 6 + bytes.fromhex(mac_address) * 16
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.sendto(data, ('<broadcast>', 9))
        log_widget.append(f"Wake-on-LAN poslané na {mac_address}.")
        return True
    except Exception as e:
        log_widget.append(f"Chyba pri posielaní Wake-on-LAN: {e}")
        return False

# --------------------------
# Funkcie pre ovládanie zásuviek (Energenie EGPMS2)
def zapni_zasuvku(cislo_zasuvky, stav_label, log_widget):
    try:
        subprocess.check_call(["syspmctl", "-o", str(cislo_zasuvky)])
        stav_label.setText("ON")
        log_widget.append(f"Zásuvka {cislo_zasuvky} bola zapnutá.")
    except subprocess.CalledProcessError as e:
        log_widget.append(f"Chyba pri zapínaní zásuvky {cislo_zasuvky}: {e}")

def vypni_zasuvku(cislo_zasuvky, stav_label, log_widget):
    try:
        subprocess.check_call(["syspmctl", "-f", str(cislo_zasuvky)])
        stav_label.setText("OFF")
        log_widget.append(f"Zásuvka {cislo_zasuvky} bola vypnutá.")
    except subprocess.CalledProcessError as e:
        log_widget.append(f"Chyba pri vypínaní zásuvky {cislo_zasuvky}: {e}")

# --------------------------
# OTA aktualizácia: prepíše súbor main.py
def perform_update(log_widget):
    update_url = 'https://github.com/jan-tdy/aplikacia8ejw8idue8wo/raw/main/main.py'
    target_path = '/home/dpv/j44softapps-socketcontrol/main.py'
    try:
        response = requests.get(update_url)
        if response.status_code == 200:
            with open(target_path, 'wb') as f:
                f.write(response.content)
            log_widget.append("Aktualizácia stiahnutá a aplikovaná.")
            log_widget.append("Zatvorte a znovu otvorte program.")
            return True
        else:
            log_widget.append("Chyba pri stahovaní aktualizácie.")
            return False
    except requests.RequestException as e:
        log_widget.append(f"Chyba pri stahovaní aktualizácie: {e}")
        return False

# --------------------------
# Funkcia pre uloženie logov
def save_logs(log_widget):
    logs_dir = '/home/dpv/j44softapps-socketcontrol'
    logs_file = os.path.join(logs_dir, 'logs.txt')
    try:
        with open(logs_file, 'a') as f:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"\n=== Log uložený: {timestamp} ===\n")
            f.write(log_widget.toPlainText())
            f.write("\n")
        log_widget.append("Logy boli uložené.")
    except Exception as e:
        log_widget.append(f"Chyba pri ukladaní logov: {e}")

# --------------------------
# Funkcia pre ovládanie strechy
def run_strecha_on(log_widget):
    target_dir = "/home/dpv/Downloads/usb-relay-hid-master/commandline/makemake"
    command = f"cd {target_dir} && ./strecha_on.sh"
    try:
        subprocess.check_call(command, shell=True)
        log_widget.append("Príkaz 'pohnut strechou' bol úspešne spustený.")
    except subprocess.CalledProcessError as e:
        log_widget.append(f"Chyba pri spúšťaní skriptu: {e}")

# --------------------------
# Hlavná GUI aplikácia
class ControlApp(QWidget):
    def __init__(self, devices):
        super().__init__()
        self.devices = devices
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Zobrazenie názvu programu
        title_label = QLabel("JadivDevControl for C14, verzia 5-2-2025_05")
        title_label.setStyleSheet("font-weight: bold; font-size: 16px;")
        layout.addWidget(title_label)

        # Sekcia Wake-on-LAN
        self.label = QLabel("Vyberte zariadenie na Wake-on-LAN:")
        layout.addWidget(self.label)

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

        # Ovládanie zásuviek
        zasuvky_label = QLabel("Lokálne ovládanie zásuviek (Energenie EGPMS2 - 4 sloty):")
        layout.addWidget(zasuvky_label)
        self.zasuvky_layout = QVBoxLayout()
        slot_names = {1: "none(1)", 2: "AZ2000(2)", 3: "C14(3)", 4: "UNKNOWN(4)"}
        for slot in range(1, 5):
            zasuvka_layout = QHBoxLayout()
            stav_label = QLabel("OFF")
            btn_on = QPushButton(f"Zapnúť {slot_names[slot]}")
            btn_on.clicked.connect(lambda checked, slot=slot, stav=stav_label: zapni_zasuvku(slot, stav, self.log_widget))
            btn_off = QPushButton(f"Vypnúť {slot_names[slot]}")
            btn_off.clicked.connect(lambda checked, slot=slot, stav=stav_label: vypni_zasuvku(slot, stav, self.log_widget))
            zasuvka_layout.addWidget(stav_label)
            zasuvka_layout.addWidget(btn_on)
            zasuvka_layout.addWidget(btn_off)
            self.zasuvky_layout.addLayout(zasuvka_layout)
        layout.addLayout(self.zasuvky_layout)

        # Ovládanie strechy
        btn_strecha_on = QPushButton("Pohnut strechou")
        btn_strecha_on.clicked.connect(lambda: run_strecha_on(self.log_widget))
        layout.addWidget(btn_strecha_on)

        # Zobrazenie webovej stránky
        self.web_view = QWebEngineView()
        self.web_view.setUrl("http://172.20.20.134")
        layout.addWidget(self.web_view)

        self.log_widget = QTextEdit()
        self.log_widget.setReadOnly(True)
        layout.addWidget(self.log_widget)

        btn_save_logs = QPushButton("Save logs")
        btn_save_logs.clicked.connect(lambda: save_logs(self.log_widget))
        layout.addWidget(btn_save_logs)

        self.setLayout(layout)
        self.setWindowTitle("JadivDevControl for C14, verzia 5-2-2025_05")
        self.resize(800, 800)
