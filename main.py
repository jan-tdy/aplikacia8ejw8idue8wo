import sys
import os
import usb.core
import usb.util
import socket
import subprocess
import requests
from datetime import datetime
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QListWidget, QTextEdit, QHBoxLayout

# Program: JadivDevControl for C14, verzia 5-2-2025_03

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
# Zapnutie: syspmctl -o {slot}
# Vypnutie: syspmctl -f {slot}
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
# OTA aktualizácia: prepíše súbor main.py na ceste /home/dpv/j44softapps-socketcontrol/main.py
def perform_update(log_widget):
    update_url = 'https://github.com/jan-tdy/aplikacia8ejw8idue8wo/raw/main/main.py'  # URL priamo na súbor
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
# Funkcia pre uloženie logov do súboru (append, s aktuálnym dátumom a časom)
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
# Funkcia pre nájdenie USB relé zariadenia (HID) 
def find_usb_relay():
    # Nájde prvé USB zariadenie - v reálnom prípade možno filtrovať podľa idVendor/idProduct
    devices = usb.core.find(find_all=True)
    for d in devices:
        # Ak by bolo potrebné filtrovať, pridajte podmienky
        return d
    return None

# Funkcia pre ovládanie USB relé
def control_usb_relay(usb_device, channel, action, log_widget):
    if usb_device is None:
        log_widget.append("USB relé zariadenie nebolo nájdené!")
        return
    try:
        # Predpokladáme, že príkaz pre kanál 1 je 0x01 a pre kanál 2 je 0x02.
        # Ak je action "on", parameter je 0x0001, ak "off", parameter je 0x0000.
        if channel == 1:
            command = 0x01
        elif channel == 2:
            command = 0x02
        else:
            log_widget.append("Neplatný kanál pre USB relé.")
            return

        value = 0x0001 if action == "on" else 0x0000
        usb_device.ctrl_transfer(0x40, command, value, 0, None)
        log_widget.append(f"USB relé kanál {channel} bol nastavený na {action}.")
    except Exception as e:
        log_widget.append(f"Chyba pri ovládaní USB relé: {e}")

# --------------------------
# Hlavná GUI aplikácia
class ControlApp(QWidget):
    def __init__(self, devices):
        super().__init__()
        self.devices = devices
        self.usb_relay = find_usb_relay()  # Nájde USB relé zariadenie
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Zobrazenie názvu programu
        title_label = QLabel("JadivDevControl for C14, verzia 5-2-2025_03")
        title_label.setStyleSheet("font-weight: bold; font-size: 16px;")
        layout.addWidget(title_label)

        # Sekcia Wake-on-LAN
        self.label = QLabel("Vyberte zariadenie na Wake-on-LAN:")
        layout.addWidget(self.label)

        self.list_widget = QListWidget()
        for device in self.devices:
            self.list_widget.addItem(f"{device['name']} - {device['mac']} - {device['ip']}")
        layout.addWidget(self.list_widget)

        self.btn_wake = QPushButton("Wake")
        self.btn_wake.clicked.connect(self.wake_device)
        layout.addWidget(self.btn_wake)

        # Lokálne ovládanie zásuviek (Energenie EGPMS2 - 4 sloty)
        zasuvky_label = QLabel("Lokálne ovládanie zásuviek (Energenie EGPMS2 - 4 sloty):")
        layout.addWidget(zasuvky_label)
        self.zasuvky_layout = QVBoxLayout()
        # Definované sloty: 1 = none(1), 2 = AZ2000(2), 3 = C14(3), 4 = UNKNOWN(4)
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

        # Ovládanie USB relé (2-kanálové)
        relay_label = QLabel("Ovládanie 2-kanálového USB relé:")
        layout.addWidget(relay_label)
        relay_layout = QHBoxLayout()
        btn_relay1_on = QPushButton("Zapnúť relé 1")
        btn_relay1_on.clicked.connect(lambda: control_usb_relay(self.usb_relay, 1, "on", self.log_widget))
        relay_layout.addWidget(btn_relay1_on)
        btn_relay1_off = QPushButton("Vypnúť relé 1")
        btn_relay1_off.clicked.connect(lambda: control_usb_relay(self.usb_relay, 1, "off", self.log_widget))
        relay_layout.addWidget(btn_relay1_off)
        btn_relay2_on = QPushButton("Zapnúť relé 2")
        btn_relay2_on.clicked.connect(lambda: control_usb_relay(self.usb_relay, 2, "on", self.log_widget))
        relay_layout.addWidget(btn_relay2_on)
        btn_relay2_off = QPushButton("Vypnúť relé 2")
        btn_relay2_off.clicked.connect(lambda: control_usb_relay(self.usb_relay, 2, "off", self.log_widget))
        relay_layout.addWidget(btn_relay2_off)
        layout.addLayout(relay_layout)

        # OTA aktualizácia
        self.btn_update = QPushButton("Aktualizovať z githubu")
        self.btn_update.clicked.connect(self.update)
        layout.addWidget(self.btn_update)

        # Log výstupy
        self.log_widget = QTextEdit()
        self.log_widget.setReadOnly(True)
        layout.addWidget(self.log_widget)

        # Tlačidlo pre uloženie logov
        btn_save_logs = QPushButton("Save logs")
        btn_save_logs.clicked.connect(lambda: save_logs(self.log_widget))
        layout.addWidget(btn_save_logs)

        self.setLayout(layout)
        self.setWindowTitle("JadivDevControl for C14, verzia 5-2-2025_03")
        self.resize(600, 800)

    def wake_device(self):
        selected = self.list_widget.currentRow()
        if selected >= 0:
            device = self.devices[selected]
            if send_wol(device['mac'], self.log_widget):
                self.log_widget.append(f"Wake-on-LAN poslané: {device['name']}")
            else:
                self.log_widget.append(f"Chyba pri odosielaní: {device['name']}")

    def update(self):
        if perform_update(self.log_widget):
            self.log_widget.append("Aplikácia bola úspešne aktualizovaná.")
        else:
            self.log_widget.append("Aktualizácia zlyhala.")

# --------------------------
# Spustenie aplikácie
if __name__ == "__main__":
    # Príklad zoznamu zariadení pre Wake-on-LAN – upravte podľa potreby
    devices = [
        {'name': 'hlavny', 'mac': 'e0:d5:5e:df:c6:4e', 'ip': '172.20.20.133'},
        {'name': 'VNT', 'mac': '78:24:af:9c:06:e7', 'ip': '172.20.20.123'},
        {'name': 'C14', 'mac': 'e0:d5:5e:37:4f:ad', 'ip': '172.20.20.103'},
        {'name': 'AZ2000', 'mac': '00:c0:08:a9:c2:32', 'ip': '172.20.20.10'},
        {'name': 'GM3000', 'mac': '00:c0:08:aa:35:12', 'ip': '172.20.20.12'}
    ]
    app = QApplication(sys.argv)
    window = ControlApp(devices)
    window.show()
    sys.exit(app.exec_())

