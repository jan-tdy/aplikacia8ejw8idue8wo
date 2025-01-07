import sys
import socket
import subprocess
import requests
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QListWidget, QLabel, QHBoxLayout, QTextEdit

# Wake-on-LAN Funkcia
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

# Funkcie pre sispmctl
def zapni_zasuvku(cislo_zasuvky, stav_label, log_widget):
    """Zapne zadanú zásuvku a aktualizuje stav."""
    try:
        subprocess.check_call(["sispmctl", "-o", str(cislo_zasuvky)])
        stav_label.setText("ON")
        log_widget.append(f"Zásuvka {cislo_zasuvky} bola zapnutá.")
    except subprocess.CalledProcessError as e:
        log_widget.append(f"Chyba pri zapínaní zásuvky {cislo_zasuvky}: {e}")

def vypni_zasuvku(cislo_zasuvky, stav_label, log_widget):
    """Vypne zadanú zásuvku a aktualizuje stav."""
    try:
        subprocess.check_call(["sispmctl", "-f", str(cislo_zasuvky)])
        stav_label.setText("OFF")
        log_widget.append(f"Zásuvka {cislo_zasuvky} bola vypnutá.")
    except subprocess.CalledProcessError as e:
        log_widget.append(f"Chyba pri vypínaní zásuvky {cislo_zasuvky}: {e}")

# OTA aktualizácia
def perform_update(log_widget):
    """Stiahne a nainštaluje aktualizáciu."""
    update_url = 'https://github.com/jan-tdy/aplikacia8ejw8idue8wo/raw/main/main.py'  # URL priamo na súbor
    try:
        response = requests.get(update_url)
        if response.status_code == 200:
            with open('main.py', 'wb') as f:
                f.write(response.content)
            log_widget.append("Aktualizácia stiahnutá a aplikovaná.")
            return True
        else:
            log_widget.append("Chyba pri stahovaní aktualizácie.")
            return False
    except requests.RequestException as e:
        log_widget.append(f"Chyba pri stahovaní aktualizácie: {e}")
        return False

# GUI aplikácia
class ControlApp(QWidget):
    def __init__(self, devices):
        super().__init__()
        self.devices = devices
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Wake-on-LAN časť
        self.label = QLabel("Vyberte zariadenie na Wake-on-LAN:")
        layout.addWidget(self.label)

        self.list_widget = QListWidget()
        for device in self.devices:
            self.list_widget.addItem(f"{device['name']} - {device['mac']} - {device['ip']}")
        layout.addWidget(self.list_widget)

        self.btn_wake = QPushButton("Wake")
        self.btn_wake.clicked.connect(self.wake_device)
        layout.addWidget(self.btn_wake)

        # Zapnutie/Vypnutie zásuviek
        self.zasuvky_layout = QVBoxLayout()

        # Názvy zásuviek
        nazvy_zasuviek = ["none(1)", "AZ2000(2)", "C14(3)", "UNKNOWN(4)"]
        stavy_zasuviek = []

        for i in range(4):
            zasuvka_layout = QHBoxLayout()
            stav_premenna = QLabel("OFF")
            stavy_zasuviek.append(stav_premenna)

            zapni_btn = QPushButton(f"Zapnúť {nazvy_zasuviek[i]}")
            zapni_btn.clicked.connect(lambda i=i, stav=stav_premenna: zapni_zasuvku(i+1, stav, self.log_widget))

            vypni_btn = QPushButton(f"Vypnúť {nazvy_zasuviek[i]}")
            vypni_btn.clicked.connect(lambda i=i, stav=stav_premenna: vypni_zasuvku(i+1, stav, self.log_widget))

            zasuvka_layout.addWidget(stav_premenna)
            zasuvka_layout.addWidget(zapni_btn)
            zasuvka_layout.addWidget(vypni_btn)
            self.zasuvky_layout.addLayout(zasuvka_layout)

        layout.addLayout(self.zasuvky_layout)

        # OTA aktualizácia
        self.btn_update = QPushButton("Aktualizovať z githubu")
        self.btn_update.clicked.connect(self.update)
        layout.addWidget(self.btn_update)

        # Log výstupy
        self.log_widget = QTextEdit()
        self.log_widget.setReadOnly(True)
        layout.addWidget(self.log_widget)

        self.setLayout(layout)
        self.setWindowTitle('Ovládanie zariadení')
        self.resize(500, 400)

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

# Zariadenia pre Wake-on-LAN
devices = [
    {'name': 'hlavny', 'mac': 'e0:d5:5e:df:c6:4e', 'ip': '172.20.20.133'},
    {'name': 'VNT', 'mac': '78:24:af:9c:06:e7', 'ip': '172.20.20.123'},
    {'name': 'C14', 'mac': 'e0:d5:5e:37:4f:ad', 'ip': '172.20.20.103'},
    {'name': 'AZ2000', 'mac': '00:c0:08:a9:c2:32', 'ip': '172.20.20.10'},
    {'name': 'GM3000', 'mac': '00:c0:08:aa:35:12', 'ip': '172.20.20.12'}
]

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ControlApp(devices)
    window.show()
    sys.exit(app.exec_())
