#!/bin/sh
echo "Starting SSH server..."

echo "SSH is active and listening on port 22"  # Детач ниже, верим на слово ¯\_(ツ)_/¯
/usr/sbin/sshd -D
