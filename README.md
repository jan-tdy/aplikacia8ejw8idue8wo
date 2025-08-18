# update
no longer supported - switch to devcontrol

# aplikacia8ejw8idue8wo
Stiahnuť main.py
Funcia ota update potrebuje internetové pripojenie
Treba nainštalovať to co je na začiatku kódu inportovane ak ešte nemate (napr pomocou pip) 
POZOR JE TO LEN PRE NÁS POČÍTAČ NA ASTRONOMICKOM OBSERVATÓRIU NA KOLONICKOM SEDLE, KTORÝ JE PRI ĎALEKOHĽAD C14. verziu pre vás vám radi spravíme, stačí napísať na j44soft@gmail.com 

----

# JadivDevControl for C14 - Verzia 7.3

JadivDevControl je aplikácia na správu zariadení v observatóriu C14. Umožňuje zapínanie a vypínanie zásuviek, posielanie WOL signálov, pohyb strechy a manuálne aktualizácie.

## 🛠️ Inštalácia
1. Uistite sa, že máte nainštalované **Python 3** a knižnicu **PyQt5**:
   ```sh
   sudo apt update
   sudo apt install python3 python3-pyqt5 wakeonlan

2. Stiahnite si najnovšiu verziu aplikácie:

git clone https://github.com/jan-tdy/aplikacia8ejw8idue8wo.git
cd aplikacia8ejw8idue8wo


3. Spustite aplikáciu:

python3 main.py

⚠️Na počítači kde ma byt je program už nainštalovaný takže stačí UPdatovat ⚠️ 

🎛️ Funkcie

1. Správa zásuviek

Zapínanie a vypínanie zásuviek syspmctl.

Aktuálny stav zásuvky sa zobrazí v GUI.

Každá akcia sa loguje.


2. Wake on LAN (WOL)

Možnosť poslať WOL paket na konkrétnu MAC adresu.


3. Ovládanie strechy

Pošle príkaz na pohyb strechy cez ./strecha_on.sh.


4. Manuálna aktualizácia

Aktualizácia prebieha len na manuálny pokyn.


5. Príkazový riadok

Pod logom je terminál, kde môžete zadať nasledovné príkazy:

6. Logovanie akcií

Každý príkaz a chyba sa zobrazí v logu.


📜 Licencia

Tento softvér je vyvíjaný ako open-source a je dostupný pod MIT licenciou.

