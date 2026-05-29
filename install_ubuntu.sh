#!/bin/bash
# install_ubuntu.sh
# Kjøres kun første gang på Ubuntu-serveren for å sette opp alt

# Finn stien der vi er nå (der ALGaE ligger)
ALGAE_DIR="$(pwd)"
CURRENT_USER="$USER"

if [ "$EUID" -eq 0 ]; then
  echo "Vennligst IKKE kjør dette skriptet som root (med sudo foran direkte)."
  echo "Kjør det som vanlig bruker, så spør skriptet om passord ved behov."
  exit
fi

echo "🚀 Setter opp ALGaE på Ubuntu..."

echo "1. Oppdaterer pakkeverktøy og installerer nødvendige avhengigheter..."
sudo apt update
sudo apt install -y software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3.11-dev portaudio19-dev git chromium-browser xinit xserver-xorg xserver-xorg-video-all xserver-xorg-legacy matchbox-window-manager x11-xserver-utils

echo "2. Setter opp virtuelt miljø (venv) med Python 3.11..."
# Hvis gammelt (feilende) venv finnes, fjern det
if [ -d "venv" ] && ! ./venv/bin/python --version | grep "3.11" > /dev/null; then
    echo "Fjerner gammelt venv..."
    rm -rf venv
fi

if [ ! -d "venv" ]; then
    python3.11 -m venv venv
fi

echo "3. Installerer Python-pakker fra requirements.txt..."
./venv/bin/pip install -r requirements.txt

echo "4. Gjør skriptene kjørbare..."
chmod +x auto_updater.sh start_kiosk.sh

echo "5. Konfigurerer X11 tilgang (slik at tjenesten kan starte grafikk)..."
sudo usermod -aG tty,video,input $CURRENT_USER
if [ -f /etc/X11/Xwrapper.config ]; then
    sudo sed -i 's/allowed_users=console/allowed_users=anybody/' /etc/X11/Xwrapper.config
    grep -q "needs_root_rights=yes" /etc/X11/Xwrapper.config || echo "needs_root_rights=yes" | sudo tee -a /etc/X11/Xwrapper.config
else
    echo "allowed_users=anybody" | sudo tee /etc/X11/Xwrapper.config
    echo "needs_root_rights=yes" | sudo tee -a /etc/X11/Xwrapper.config
fi

echo "6. Setter opp ALGaE som en bakgrunnstjeneste (systemd)..."
# Lager en kopi av service-filen hvor vi setter inn riktig bruker og mappe
sed "s|INSERT_USER|$CURRENT_USER|g; s|INSERT_DIR|$ALGAE_DIR|g" algae.service > /tmp/algae.service
sudo mv /tmp/algae.service /etc/systemd/system/algae.service

# Last inn systemd på nytt og aktiver tjenesten
sudo systemctl daemon-reload
sudo systemctl enable algae.service
sudo systemctl start algae.service

echo "7. Setter opp automatisk oppdatering (hvert 15. minutt)..."
# Fjerner gammel cron-jobb om den finnes, og legger til ny
(crontab -l 2>/dev/null | grep -v "auto_updater.sh"; echo "*/15 * * * * $ALGAE_DIR/auto_updater.sh >> $ALGAE_DIR/updater.log 2>&1") | crontab -

echo ""
echo "✅ ALGaE ER NÅ FERDIG SATT OPP OG KJØRER I BAKGRUNNEN!"
echo "--------------------------------------------------------"
echo "👉 For å se hva ALGaE driver med (loggen), skriv:"
echo "   journalctl -u algae -f"
echo ""
echo "👉 For å se oppdaterings-loggen, skriv:"
echo "   cat $ALGAE_DIR/updater.log"
echo ""
echo "For å starte ALGaE på nytt manuelt:"
echo "   sudo systemctl restart algae"
