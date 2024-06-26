import subprocess
import shutil
import os
import time

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
        print(f"Error executing lsblk: {e}")

    return list(connected_drives)

def get_drive_storage(drives):
    drive_storage_info = []
    for drive_info in drives:
        try:
            usage = shutil.disk_usage(drive_info[1])
            drive_storage_info.append((drive_info[0], drive_info[1], usage.total))
        except Exception as e:
            print(f"Error getting disk usage for {drive_info[1]}: {e}")

    return drive_storage_info

def create_spiti_folder(drive_info):
    spiti_folder_path = os.path.join(drive_info[1], 'spiti')

    try:
        os.makedirs(spiti_folder_path, exist_ok=True)
        print(f"Folder 'spiti' created successfully at {spiti_folder_path}")
    except Exception as e:
        print(f"Error creating folder 'spiti': {e}")

def create_card_folder(spiti_folder_path):
    # Find the last created card folder
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
        print(f"Folder '{new_card_folder}' created successfully at {new_card_folder_path}")
    except Exception as e:
        print(f"Error creating folder '{new_card_folder}': {e}")

    return new_card_folder_path

def copy_data_to_card_folder(source_drive, card_folder_path):
    start_time = time.time()

    try:
        if os.path.exists(card_folder_path):
            print(f"Folder '{os.path.basename(card_folder_path)}' already exists. Removing it.")
            shutil.rmtree(card_folder_path)

        shutil.copytree(source_drive, card_folder_path)
        print(f"Data copied successfully to {card_folder_path}")

        end_time = time.time()
        total_time = end_time - start_time
        print(f"Total time taken: {total_time:.2f} seconds")
    except Exception as e:
        print(f"Error copying data: {e}")


# Example usage
connected_drives = get_connected_drives()
print("Connected USB drives:")
for drive_info in connected_drives:
    print(drive_info)

drive_storage_info = get_drive_storage(connected_drives)
print("Storage information for each connected USB drive:")
for drive_info in drive_storage_info:
    print(f"Drive: {drive_info[0]}, Mount Point: {drive_info[1]}, Total Storage: {drive_info[2] / (1024 ** 3):.2f} GB")

# Find the drives with the largest and smallest storage
largest_drive_info = max(drive_storage_info, key=lambda x: x[2])
smallest_drive_info = min(drive_storage_info, key=lambda x: x[2])

# Create 'spiti' folder in the drive with the largest storage
create_spiti_folder(largest_drive_info)

# Create 'card-{number}' folder inside 'spiti'
spiti_folder_path = os.path.join(largest_drive_info[1], 'spiti')
card_folder_path = create_card_folder(spiti_folder_path)

# Copy data from the drive with smaller storage to the 'card' folder
copy_data_to_card_folder(smallest_drive_info[1], card_folder_path)
