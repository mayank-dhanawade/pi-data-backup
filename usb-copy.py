import subprocess

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

# Example usage
connected_drives = get_connected_drives()
print("Connected USB drives:")
for drive_info in connected_drives:
    print(drive_info)
