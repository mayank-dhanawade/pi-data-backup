#!/usr/bin/env python3
import subprocess
import os
import time
import logging
import sys
sys.stdout.flush()


def setup_logger(log_file_path):
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # Create a file handler and set the level to debug
    fh = logging.FileHandler(log_file_path)
    fh.setLevel(logging.DEBUG)

    # Remove the console handler setup

    # Create a formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)

    # Add the file handler to the logger
    logger.addHandler(fh)
    logging.info("Script started")
    logging.info(f"Process ID: {os.getpid()}")

def get_connected_drives():
    connected_drives = set()

    try:
        lsblk_output = subprocess.check_output(['lsblk', '-o', 'NAME,MOUNTPOINT'])
        lsblk_output = lsblk_output.decode('utf-8')
        print(f"Raw lsblk output:\n{lsblk_output}")

        lsblk_lines = lsblk_output.split('\n')[1:]
        for line in lsblk_lines:
            columns = line.split()
            if len(columns) == 2 and '/media/mayank/' in columns[1]:
                drive_name = columns[0]
                mount_point = columns[1]
                connected_drives.add((drive_name, mount_point))

    except subprocess.CalledProcessError as e:
        logging.error(f"Error executing lsblk: {e}")

    return list(connected_drives)

def wait_for_new_disk(initial_connected_drives, timeout_seconds=60):
    logging.info(f"inside wait for new disk before connect")
    connected_drives_before = set(initial_connected_drives)
    start_time = time.time()
    logging.info(f"inside wait for new disk after connect")

    try:
        while time.time() - start_time < timeout_seconds:
            logging.info("inside while loop before sleep")
            time.sleep(5)  # Adjust the sleep interval as needed
            logging.info("inside while loop after sleep")

            logging.getLogger().handlers[0].flush()  # Force a flush

            connected_drives_after = set(get_connected_drives())
            new_disks = connected_drives_after - connected_drives_before

            logging.info(f"Connected drives before: {connected_drives_before}")
            logging.info(f"Connected drives after : {connected_drives_after}")
            logging.info(f"New disks detected     : {new_disks}")

            if new_disks:
                logging.info("New USB drive detected:")
                for drive_info in new_disks:
                    logging.info(drive_info)
                return connected_drives_after
    except Exception as e:
        logging.error(f"Error in wait for: {e}")
    logging.warning("Timeout reached. No new USB drive detected within the specified time.")
    return connected_drives_before

def get_drive_storage(drives):
    drive_storage_info = []
    for drive_info in drives:
        try:
            usage = subprocess.check_output(['df', '--output=size', drive_info[1]])
            usage = int(usage.decode('utf-8').split('\n')[1]) * 1024  # Convert to bytes
            drive_storage_info.append((drive_info[0], drive_info[1], usage))
        except subprocess.CalledProcessError as e:
            logging.error(f"Error getting disk usage for {drive_info[1]}: {e}")

    return drive_storage_info

def create_spiti_folder(drive_info):
    spiti_folder_path = os.path.join(drive_info[1], 'spiti')

    try:
        os.makedirs(spiti_folder_path, exist_ok=True)
        logging.info(f"Folder 'spiti' created successfully at {spiti_folder_path}")
    except Exception as e:
        logging.error(f"Error creating folder 'spiti': {e}")

def create_card_folder(spiti_folder_path):
    existing_card_folders = [folder for folder in os.listdir(spiti_folder_path) if folder.startswith('card-')]
    existing_card_numbers = [int(folder.split('-')[1]) for folder in existing_card_folders]

    if existing_card_numbers:
        next_card_number = max(existing_card_numbers) + 1
    else:
        next_card_number = 1

    new_card_folder = f"card-{next_card_number}"
    new_card_folder_path = os.path.join(spiti_folder_path, new_card_folder)

    try:
        os.makedirs(new_card_folder_path, exist_ok=True)
        logging.info(f"Folder '{new_card_folder}' created successfully at {new_card_folder_path}")
    except Exception as e:
        logging.error(f"Error creating folder '{new_card_folder}': {e}")

    return new_card_folder_path

def rsync_copy_data(source_drive, destination_folder):
    start_time = time.time()

    try:
        subprocess.run(['rsync', '-a', '--info=progress2', source_drive + '/', destination_folder])
        logging.info(f"Data copied successfully to {destination_folder}")

        end_time = time.time()
        total_time = end_time - start_time
        logging.info(f"Total time taken: {total_time:.2f} seconds")
    except subprocess.CalledProcessError as e:
        logging.error(f"Error copying data: {e}")

def is_drive_mounted(mount_point):
    try:
        # Run the 'findmnt' command to check if the mount point exists
        subprocess.check_output(['findmnt', '--mountpoint', mount_point])
        return True
    except subprocess.CalledProcessError:
        return False

if __name__ == "__main__":
    try:
        # Change directory to the script location
        script_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(script_dir)

        

        # Set up logging in the 'log' folder within the script's directory
        log_folder_path = os.path.join(script_dir, 'log')
        os.makedirs(log_folder_path, exist_ok=True)

        timestamp = time.strftime("%Y%m%d_%H%M%S")
        log_file_path = os.path.join(log_folder_path, f"log_{timestamp}.txt")

        # Redirect stdout and stderr to a log file
        sys.stdout = open(log_file_path, 'w')
        sys.stderr = sys.stdout

        setup_logger(log_file_path)
        # Example usage
        connected_drives_before = get_connected_drives()

        logging.info("Connected USB drives before waiting:")
        for drive_info in connected_drives_before:
            logging.info(drive_info)

        # Wait for the new disk to be mounted
        connected_drives_after = wait_for_new_disk(connected_drives_before, timeout_seconds=60)

        logging.info("Connected USB drives after waiting:")
        for drive_info in connected_drives_after:
            logging.info(drive_info)

        drive_storage_info = get_drive_storage(connected_drives_after)
        logging.info("Storage information for each connected USB drive:")
        for drive_info in drive_storage_info:
            logging.info(f"Drive: {drive_info[0]}, Mount Point: {drive_info[1]}, Total Storage: {drive_info[2] / (1024 ** 3):.2f} GB")

        if len(connected_drives_after) >= 2:
            largest_drive_info = max(drive_storage_info, key=lambda x: x[2])
            create_spiti_folder(largest_drive_info)

            spiti_folder_path = os.path.join(largest_drive_info[1], 'spiti')
            card_folder_path = create_card_folder(spiti_folder_path)

            smallest_drive_info = min(drive_storage_info, key=lambda x: x[2])
            rsync_copy_data(smallest_drive_info[1], card_folder_path)
        else:
            logging.warning("At least two USB drives are required for the operation.")
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        raise  # Raise the exception again for debugging purposes
