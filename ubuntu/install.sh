#!/usr/bin/env bash
set -euo pipefail
sudo apt update
sudo apt install -y openssh-server fail2ban python3-systemd
sudo systemctl enable --now ssh
sudo systemctl status ssh --no-pager
whoami
ip -br a
echo 'Installation complete. Follow README.md to run the baseline before enabling protection.'
