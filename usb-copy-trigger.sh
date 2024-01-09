#!/bin/bash

# Create a new file when a USB device is connected
echo "A USB device has been connected to your Raspberry Pi 5." > /home/mayank/workspace/pi-data-backup/usb_connected.txt


nohup /home/mayank/workspace/pi-data-backup/copy-script.sh > /home/mayank/workspace/pi-data-backup/usb-copy-trigger-log.txt 2>&1 &
