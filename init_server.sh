#!/usr/bin/env bash
set -euo pipefail

if [[ $(id -u) -ne 0 ]]; then
  echo "This script must be run as root." >&2
  exit 1
fi

log() {
  echo "[init_server] $1"
}

log "Updating system packages"
apt-get update -y
apt-get upgrade -y

SWAP_FILE="/swapfile"
if ! swapon --show | grep -q "$SWAP_FILE"; then
  log "Creating 16G swap at $SWAP_FILE"
  fallocate -l 16G "$SWAP_FILE"
  chmod 600 "$SWAP_FILE"
  mkswap "$SWAP_FILE"
  swapon "$SWAP_FILE"
  if ! grep -q "$SWAP_FILE" /etc/fstab; then
    echo "$SWAP_FILE none swap sw 0 0" >> /etc/fstab
  fi
else
  log "Swap file already active"
fi

log "Installing Docker prerequisites"
apt-get install -y ca-certificates curl gnupg lsb-release

install -m 0755 -d /etc/apt/keyrings
if [ ! -f /etc/apt/keyrings/docker.gpg ]; then
  curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
fi
chmod a+r /etc/apt/keyrings/docker.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" \
  | tee /etc/apt/sources.list.d/docker.list > /dev/null

log "Installing Docker Engine and Docker Compose plugin"
apt-get update -y
apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

log "Creating project directories"
install -d -m 755 /opt/sodmaster/traefik
install -d -m 755 /opt/sodmaster/data

log "Ensuring script is executable"
chmod +x "$0"

log "Initialization complete"
