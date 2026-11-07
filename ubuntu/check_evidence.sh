#!/usr/bin/env bash
set -euo pipefail
sudo journalctl -u ssh.service --since '10 minutes ago' --no-pager -o cat
sudo fail2ban-client status sshd
if sudo test -f /var/log/fail2ban.log; then
    sudo tail -n 40 /var/log/fail2ban.log
else
    sudo journalctl -u fail2ban --since '10 minutes ago' --no-pager
fi
