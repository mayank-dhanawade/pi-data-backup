#!/bin/bash

# Change directory to the script location
cd "$(dirname "$0")"

# Capture environment information to a log file
env > /home/mayank/workspace/pi-data-backup/copy-script-env.log

# Create a new file when a USB device is connected
echo "copy script initiated" > /home/mayank/workspace/pi-data-backup/usb_copy_initiated.txt

# Redirect both stdout and stderr to a log file
exec &> /home/mayank/workspace/pi-data-backup/copy-script.log

# Print the start time
echo "Script started at $(date)"

# Print the current working directory
echo "Current working directory: $(pwd)"

# Print the list of files in the current directory
echo "List of files in the current directory:"
ls -la

# Run the Python script with the absolute path
/usr/bin/python3 /home/mayank/workspace/pi-data-backup/usb-copy.py >> /home/mayank/workspace/pi-data-backup/usb_copy_python_log.txt 2>&1

# Print the end time
echo "Script ended at $(date)"
