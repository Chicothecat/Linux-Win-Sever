#!/usr/bin/env bash
set -euo pipefail
lab_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
target=/etc/fail2ban/jail.d/sshd.local
if sudo test -f "$target"; then
    sudo cp -a "$target" "${target}.backup.$(date +%Y%m%d%H%M%S)"
fi
sudo install -m 644 "$lab_dir/config/sshd.local" "$target"
sudo fail2ban-client -t
sudo systemctl enable --now fail2ban
sudo systemctl restart fail2ban
sudo fail2ban-client status sshd
sudo fail2ban-client get sshd maxretry
