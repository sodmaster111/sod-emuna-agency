# SOD Master – Phase 1 Bootstrap

This repository provides the bare minimum required to bring up the shared infrastructure proxy (Traefik) on a fresh Ubuntu 24.04 server.

## 1. Connect to the server via SSH
```bash
ssh <user>@<server-ip>
```
Use the administrative user with sudo/root access.

## 2. Clone the repository
```bash
cd /opt
sudo git clone https://github.com/<your-org>/sod-emuna-agency.git
cd sod-emuna-agency
```
(Replace the URL if you are using a fork or private mirror.)

## 3. Initialize the server
```bash
sudo bash init_server.sh
```
This script updates the OS, creates a 16 GB swap file, installs Docker + Docker Compose, and prepares `/opt/sodmaster` directories.

## 4. Launch Traefik
```bash
sudo docker compose up -d
```
The Traefik dashboard will then be available on port `8080`, while HTTP/HTTPS traffic is handled on ports `80` and `443` with automatic Let's Encrypt certificates for `sodmaster.online`.
