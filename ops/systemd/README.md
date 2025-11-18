# SOD API systemd service

This directory contains the `sod-api.service` unit file for running the SOD API with `uvicorn` from `/opt/sod-emuna-agency`.

## Installation
1. Copy the unit file to the systemd directory:
   ```bash
   sudo cp ops/systemd/sod-api.service /etc/systemd/system/sod-api.service
   ```
2. Reload systemd units:
   ```bash
   sudo systemctl daemon-reload
   ```

## Usage
- Enable the service to start on boot:
  ```bash
  sudo systemctl enable sod-api.service
  ```
- Start the service:
  ```bash
  sudo systemctl start sod-api.service
  ```
- Check the service status:
  ```bash
  sudo systemctl status sod-api.service
  ```
