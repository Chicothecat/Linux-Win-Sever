"""Controlled SSH password-list experiment for the report's isolated lab."""
import argparse
import getpass
import socket
import time
from pathlib import Path

import paramiko


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--host', default='192.168.232.131')
    parser.add_argument('--user', default='lab')
    parser.add_argument('--port', type=int, default=22)
    parser.add_argument('--known-hosts', type=Path,
                        default=Path.home() / '.ssh' / 'known_hosts')
    args = parser.parse_args()
    if not args.known_hosts.is_file():
        parser.error('Missing known_hosts. Verify the server fingerprint and connect with ssh first.')
    correct_password = getpass.getpass('Lab account password (control sample): ')
    if not correct_password:
        parser.error('The control password must not be empty.')
    # Ten deliberately incorrect samples followed by the supplied control.
    wrong = [f'lab-wrong-sample-{i:02d}' for i in range(1, 12)
             if f'lab-wrong-sample-{i:02d}' != correct_password][:10]
    for attempt, password in enumerate(wrong + [correct_password], start=1):
        client = paramiko.SSHClient()
        client.load_host_keys(str(args.known_hosts))
        client.set_missing_host_key_policy(paramiko.RejectPolicy())
        try:
            client.connect(args.host, port=args.port, username=args.user,
                           password=password, look_for_keys=False, allow_agent=False,
                           timeout=5, banner_timeout=5, auth_timeout=5)
            print(f'Attempt {attempt}: authenticated successfully.')
            return 0
        except paramiko.AuthenticationException:
            print(f'Attempt {attempt}: authentication failed.')
        except paramiko.BadHostKeyException:
            print('Server host key changed. Verify the server identity before continuing.')
            return 2
        except (paramiko.SSHException, socket.timeout, OSError) as exc:
            print(f'Attempt {attempt}: connection error ({type(exc).__name__}): {exc}')
            print('Check Fail2ban logs and banned IPs; this error alone does not prove a ban.')
            return 2
        finally:
            client.close()
        time.sleep(1)
    print('No sample authenticated successfully.')
    return 1


if __name__ == '__main__':
    raise SystemExit(main())
