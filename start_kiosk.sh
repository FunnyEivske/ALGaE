#!/bin/bash
# start_kiosk.sh
# Dette skriptet starter X-serveren og setter opp Chromium i kiosk-modus

# Tving oppsett av riktig Runtime Dir for Snap
export XDG_RUNTIME_DIR=/run/user/$(id -u)
if [ ! -d "$XDG_RUNTIME_DIR" ]; then
  mkdir -p "$XDG_RUNTIME_DIR"
  chmod 0700 "$XDG_RUNTIME_DIR"
fi

# Sørg for at XDG_RUNTIME_DIR finnes (viktig for Wayland/Snap)
export XDG_RUNTIME_DIR=/run/user/$(id -u)

# Kiosk-løkke: Bruk 'cage' (Wayland-basert kiosk) i stedet for gammeldags X11.
# Dette løser 99% av alle sikkerhetskrasj med Snap Chromium på Ubuntu Server.
while true; do
  echo "Starter Cage og Chromium..."
  cage -d -s -- chromium-browser --kiosk http://localhost:8080 --no-sandbox --disable-infobars --window-position=0,0 --window-size=1920,1080
  sleep 5
done
