#!/usr/bin/env python3
import subprocess
import os
import time
import logging

def setup_logger(log_file_path):
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # Create a file handler and set the level to debug
    fh = logging.FileHandler(log_file_path)
    fh.setLevel(logging.DEBUG)

    # Create a console handler and set the level to debug
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    # Create a formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    # Add the handlers to the logger
    logger.addHandler(fh)
    logger.addHandler(ch)

def get_connected_drives():
    connected_drives = set()

    try:
        lsblk_output = subprocess.check_output(['lsblk', '-o', 'NAME,MOUNTPOINT'])
        lsblk_output = lsblk_output.decode('utf-8').split('\n')

        for line in lsblk_output[1:]:
            columns = line.split()
            if len(columns) == 2 and '/media/mayank/' in columns[1]:
                drive_name = columns[0]
                mount_point = columns[1]
                connected_drives.add((drive_name, mount_point))

    except subprocess.CalledProcessError as e:
        logging.error(f"Error executing lsblk: {e}")

    return list(connected_drives)

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

if __name__ == "__main__":
    # Example usage
    connected_drives = get_connected_drives()
    
    # Check if at least two drives are connected
    if len(connected_drives) >= 2:
        # Set up logging in the 'log' folder within the script's directory
        log_folder_path = os.path.join(os.getcwd(), 'log')
        os.makedirs(log_folder_path, exist_ok=True)

        timestamp = time.strftime("%Y%m%d_%H%M%S")
        log_file_path = os.path.join(log_folder_path, f"log_{timestamp}.txt")
        setup_logger(log_file_path)

        logging.info("Connected USB drives:")
        for drive_info in connected_drives:
            logging.info(drive_info)

        drive_storage_info = get_drive_storage(connected_drives)
        logging.info("Storage information for each connected USB drive:")
        for drive_info in drive_storage_info:
            logging.info(f"Drive: {drive_info[0]}, Mount Point: {drive_info[1]}, Total Storage: {drive_info[2] / (1024 ** 3):.2f} GB")

        largest_drive_info = max(drive_storage_info, key=lambda x: x[2])
        create_spiti_folder(largest_drive_info)

        spiti_folder_path = os.path.join(largest_drive_info[1], 'spiti')
        card_folder_path = create_card_folder(spiti_folder_path)

        smallest_drive_info = min(drive_storage_info, key=lambda x: x[2])
        rsync_copy_data(smallest_drive_info[1], card_folder_path)
    else:
        logging.warning("At least two USB drives are required for the operation.")
