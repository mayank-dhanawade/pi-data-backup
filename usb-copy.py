import subprocess
import shutil

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

# Example usage
connected_drives = get_connected_drives()
print("Connected USB drives:")
for drive_info in connected_drives:
    print(drive_info)

drive_storage_info = get_drive_storage(connected_drives)
print("Storage information for each connected USB drive:")
for drive_info in drive_storage_info:
    print(f"Drive: {drive_info[0]}, Mount Point: {drive_info[1]}, Total Storage: {drive_info[2] / (1024 ** 3):.2f} GB")
