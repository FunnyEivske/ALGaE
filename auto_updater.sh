#!/bin/bash
# Hent mappen skriptet ligger i, og gå dit
cd "$(dirname "$0")" || exit

# Hent nyeste info fra git
git fetch origin

# Sjekk hvilken branch vi er på
BRANCH=$(git rev-parse --abbrev-ref HEAD)

# Sammenlign lokal og remote (github) versjon
LOCAL=$(git rev-parse @)
REMOTE=$(git rev-parse @{u})

if [ "$LOCAL" != "$REMOTE" ]; then
    echo "Ny versjon oppdaget på GitHub!"
    
    # 1. Vis oppdateringsanimasjonen ved å sende POST til server.py
    curl -X POST http://localhost:8080/api/state \
         -H "Content-Type: application/json" \
         -d '{"state": "updating"}'
    
    # Gi animasjonen litt tid til å vises før vi dreper serveren
    sleep 5
    
    # 2. Trekk ned den nye koden
    git pull origin "$BRANCH"
    
    # 3. Restart tjenesten
    echo "Restarter ALGaE for å ta i bruk den nye versjonen..."
    sudo systemctl restart algae
else
    echo "ALGaE er allerede oppdatert."
fi
