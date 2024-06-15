#!/bin/bash


# Replace with your server's SSH username and IP address or hostname
SERVER_SSH_USER="root"
SERVER_IP="159.203.188.95"
DESTINATION_PATH="/root"
CURRENT_DIR_NAME="$(basename "$PWD")"
FINAL_PATH="/root/deuz-server"

# Compress all files and folders in the current directory excluding this script
tar --exclude="$0" -czvf "${CURRENT_DIR_NAME}".tar.gz .

# Transfer the compressed file
scp "${CURRENT_DIR_NAME}".tar.gz "$SERVER_SSH_USER"@"$SERVER_IP":"$DESTINATION_PATH"

# Clean up the compressed file from local machine if needed
rm "${CURRENT_DIR_NAME}".tar.gz

ssh "$SERVER_SSH_USER"@"$SERVER_IP" << EOF
tar -xzvf "${CURRENT_DIR_NAME}".tar.gz -C "${FINAL_PATH}"
EOF
