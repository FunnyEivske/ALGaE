#!/bin/bash
# start_kiosk.sh
# Dette skriptet starter X-serveren og setter opp Chromium i kiosk-modus

# Tving oppsett av riktig Runtime Dir for Snap
export XDG_RUNTIME_DIR=/run/user/$(id -u)
if [ ! -d "$XDG_RUNTIME_DIR" ]; then
  mkdir -p "$XDG_RUNTIME_DIR"
  chmod 0700 "$XDG_RUNTIME_DIR"
fi

# Lag konfigurasjonsfil for X-serveren (hva som skal kjøre på skjermen)
cat << 'EOF' > ~/.xinitrc
#!/bin/bash
# 1. Skru av strømsparing og skjermsparer
xset s off
xset s noblank
xset -dpms

# 2. Start den lette vindusbehandleren (tvinger fullskjerm)
matchbox-window-manager -use_titlebar no &

# 3. Start nettleseren i en evig løkke, slik at den spretter opp igjen hvis den kræsjer
while true; do
  chromium-browser --kiosk http://localhost:8080 --no-sandbox --disable-infobars --window-position=0,0 --window-size=1920,1080
  sleep 5
done
EOF

chmod +x ~/.xinitrc

# Start selve X-serveren (grafikkmotoren) på TTY7, og skjul musepekeren
startx ~/.xinitrc -- -nocursor vt7
