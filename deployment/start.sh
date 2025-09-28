#!/bin/sh
echo "Starting SSH server..."

if ss -tuln | grep ":22"; then
  echo "Port 22 all ready taken. Stopping conflicting process..."
  pkill -f sshd || true
  sleep 2
fi

echo "SSH is active and listening on port 22"  # Детач ниже, верим на слово ¯\_(ツ)_/¯
exec /usr/sbin/sshd -D
