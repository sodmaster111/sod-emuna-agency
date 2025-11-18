# SOD Prayer Bot systemd service

This document explains how to install and manage the `sod-prayer-bot.service` unit for running the Hebrew daily prayer Telegram bot from `/opt/sod-emuna-agency`.

## Installation
1. Copy the unit file to the systemd directory:
   ```bash
   sudo cp ops/systemd/sod-prayer-bot.service /etc/systemd/system/sod-prayer-bot.service
   ```
2. Reload systemd units:
   ```bash
   sudo systemctl daemon-reload
   ```

## Usage
- Enable the service to start on boot:
  ```bash
  sudo systemctl enable sod-prayer-bot.service
  ```
- Start or restart the service:
  ```bash
  sudo systemctl restart sod-prayer-bot.service
  ```
- Check the service status:
  ```bash
  sudo systemctl status sod-prayer-bot.service
  ```
- View recent logs:
  ```bash
  sudo journalctl -u sod-prayer-bot.service -n 100 -f
  ```
