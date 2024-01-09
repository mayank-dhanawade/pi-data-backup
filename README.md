# pi-data-backup
This repo is used to copy data from one drive to another


//udev rules
# Run script when device is added
ACTION=="add", SUBSYSTEM=="block", SUBSYSTEMS=="usb", RUN+="/home/mayank/workspace/pi-data-backup/usb-copy-trigger.sh"

# Run script when device is removed
ACTION=="remove", SUBSYSTEM=="block", SUBSYSTEMS=="usb", RUN+="/home/mayank/workspace/pi-data-backup/usb-copy-trigger.sh"
