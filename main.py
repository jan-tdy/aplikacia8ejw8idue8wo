import sys
import os
import socket
import subprocess
import requests
import webbrowser
from datetime import datetime
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QListWidget, QTextEdit, QHBoxLayout, QLineEdit, QTabWidget

# Program: JadivDevControl for C14, verzia 5.1

class ControlApp(QWidget):
    def __init__(self, devices):
        super().__init__()
        self.devices = devices
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.tabs = QTabWidget()

        # Karta Wake-on-LAN
        self.tab_wol = QWidget()
        self.init_wol_ui()
        self.tabs.addTab(self.tab_wol, "Wake-on-LAN")

        # Karta Zásuvky
        self.tab_zasuvky = QWidget()
        self.init_zasuvky_ui()
        self.tabs.addTab(self.tab_zasuvky, "Zásuvky")

        # Karta Strecha
        self.tab_strecha = QWidget()
        self.init_strecha_ui()
        self.tabs.addTab(self.tab_strecha, "Strecha")

        # Karta Kamera
        self.tab_kamera = QWidget()
        self.init_kamera_ui()
        self.tabs.addTab(self.tab_kamera, "Kamera")

        # Karta Logy
        self.tab_logy = QWidget()
        self.init_logy_ui()
        self.tabs.addTab(self.tab_logy, "Logy")

        # Karta About
        self.tab_about = QWidget()
        self.init_about_ui()
        self.tabs.addTab(self.tab_about, "About")

        layout.addWidget(self.tabs)
        self.setLayout(layout)
        self.setWindowTitle("JadivDevControl for C14, verzia 5.1")
        self.resize(800, 600)

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

    def init_zasuvky_ui(self):
        layout = QVBoxLayout()
        slot_names = {1: "none(1)", 2: "AZ2000(2)", 3: "C14(3)", 4: "UNKNOWN(4)"}
        for slot in range(1, 5):
            zasuvka_layout = QHBoxLayout()
            stav_label = QLabel("OFF")
            btn_on = QPushButton(f"Zapnúť {slot_names[slot]}")
            btn_off = QPushButton(f"Vypnúť {slot_names[slot]}")
            zasuvka_layout.addWidget(stav_label)
            zasuvka_layout.addWidget(btn_on)
            zasuvka_layout.addWidget(btn_off)
            layout.addLayout(zasuvka_layout)
        self.tab_zasuvky.setLayout(layout)

    def init_strecha_ui(self):
        layout = QVBoxLayout()
        btn_strecha_on = QPushButton("Pohnut strechou")
        btn_strecha_on.clicked.connect(self.run_strecha_on)
        layout.addWidget(btn_strecha_on)
        self.tab_strecha.setLayout(layout)

    def init_kamera_ui(self):
        layout = QVBoxLayout()
        btn_open_cam = QPushButton("Otvoriť kameru")
        btn_open_cam.clicked.connect(lambda: webbrowser.open("http://172.20.20.134"))
        layout.addWidget(btn_open_cam)
        self.tab_kamera.setLayout(layout)

    def init_logy_ui(self):
        layout = QVBoxLayout()
        self.log_widget = QTextEdit()
        self.log_widget.setReadOnly(True)
        layout.addWidget(self.log_widget)
        btn_save_logs = QPushButton("Save logs")
        btn_save_logs.clicked.connect(self.save_logs)
        layout.addWidget(btn_save_logs)
        self.tab_logy.setLayout(layout)

    def init_about_ui(self):
        layout = QVBoxLayout()
        about_label = QLabel("""
        JadivDevControl for C14, verzia 5.1
        Stiahnuť main.py
        Funkcia OTA update potrebuje internetové pripojenie.
        Treba nainštalovať všetky závislosti cez pip.
        
        ⚠️ Tento program je určený LEN pre počítač na observatóriu Kolonické sedlo
        pri ďalekohľade C14.
        
        Verziu pre vaše použitie vám radi vytvoríme, kontaktujte nás na:
        📧 j44soft@gmail.com
        
        🆕 Zmeny vo verzii 5.1
        ✅ Odstránený QWebEngineView, čím sa eliminujú závislosti na PyQtWebEngine.
        ✅ Pridané tlačidlo „Otvoriť kameru“, ktoré spustí predvolený prehliadač.
        """)
        layout.addWidget(about_label)
        self.tab_about.setLayout(layout)

    def wake_device(self):
        selected = self.list_widget.currentRow()
        mac_address = self.mac_input.text().strip()
        if selected >= 0:
            device = self.devices[selected]
            mac_address = device['mac']
        if mac_address:
            send_wol(mac_address, self.log_widget)
        else:
            self.log_widget.append("Nezadaná MAC adresa!")

    def run_strecha_on(self):
        subprocess.run(["/home/dpv/Downloads/usb-relay-hid-master/commandline/makemake/strecha_on.sh"], shell=True)

    def save_logs(self):
        pass  # Implementovať ukladanie logov

if __name__ == "__main__":
    devices = [
        {'name': 'hlavny', 'mac': 'e0:d5:5e:df:c6:4e', 'ip': '172.20.20.133'},
        {'name': 'VNT', 'mac': '78:24:af:9c:06:e7', 'ip': '172.20.20.123'},
    ]
    app = QApplication(sys.argv)
    window = ControlApp(devices)
    window.show()
    sys.exit(app.exec_())
