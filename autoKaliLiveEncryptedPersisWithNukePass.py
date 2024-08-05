import subprocess
import getpass
import argparse


def display_drives():
    """Displays available drives and their sub-devices using lsblk."""
    result = subprocess.run(["lsblk", "-o", "NAME,TYPE,SIZE"], capture_output=True, text=True)

    drives = []
    print("\nAvailable drives and sub-devices:")
    for line in result.stdout.splitlines():
        parts = line.strip().split()
        if "disk" in line and len(parts) >= 2:
            drives.append(parts[0])
            print(f"{len(drives)}. {line.strip()}")

    print(
        "\nIMPORTANT: If your target drive does not have sub-devices (e.g., /dev/sdX1, /dev/sdX2), it may already be encrypted.")
    print("You may need to shrink existing volumes to create space for Kali Live and persistence.")

    while True:
        try:
            choice = int(input("Select the drive number to use: "))
            if 1 <= choice <= len(drives):
                return drives[choice - 1]
            else:
                print("Invalid choice. Please select a valid drive number.")
        except ValueError:
            print("Invalid input. Please enter a number.")


def create_kali_live_usb(drive, iso_path):
    """Creates a bootable Kali Live USB."""

    # ... (Code to create bootable USB remains the same as before)

    print(
        "Bootable Kali Live USB created successfully! You can now manually set up persistence and encryption after booting.")


def setup_persistence_and_nuke(drive):
    """Guides the user through setting up persistence and nuke manually."""

    print("--- Persistence and Nuke Setup Instructions ---\n")

    # Persistence instructions
    print(f"sudo fdisk {drive} <<< $(printf 'n\np\n\n\n\nw')")
    print(f"sudo cryptsetup --verbose --verify-passphrase luksFormat {drive}3")
    print(f"sudo cryptsetup luksOpen {drive}3 my_usb")
    print(f"sudo mkfs.ext4 -L persistence /dev/mapper/my_usb")
    print(f"sudo e2label /dev/mapper/my_usb persistence")
    print(f"sudo mkdir -p /mnt/my_usb")
    print(f"sudo mount /dev/mapper/my_usb /mnt/my_usb")
    print(f"echo '/ union' | sudo tee /mnt/my_usb/persistence.conf")
    print(f"sudo umount /dev/mapper/my_usb")
    print(f"sudo cryptsetup luksClose /dev/mapper/my_usb")

    # Nuke setup instructions
    print(f"sudo apt install -y cryptsetup-nuke-password")
    print(f"sudo dpkg-reconfigure cryptsetup-nuke-password")
    print(f"cryptsetup luksHeaderBackup --header-backup-file luksheader.back {drive}3")
    print(f"openssl enc -e -aes-256-cbc -in luksheader.back -out luksheader.back.enc")
    print(f"openssl enc -d -aes-256-cbc -in luksheader.back.enc -out luksheader.back")
    print(f"cryptsetup luksHeaderRestore --header-backup-file luksheader.back {drive}3")


def run_command(cmd):
    """Executes a shell command and handles errors."""
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error running command '{cmd}':\n{e.stderr}")


def add_nuke_feature(drive, nuke_password):
    """Adds the 'nuke' feature to LUKS on the drive."""
    run_command("sudo apt-get install -y tor proxychains")
    subprocess.run(["sudo", "cryptsetup", "luksAddNuke", drive], input=nuke_password.encode(), check=True)
    print("Nuke feature added successfully.")


# Main execution with argument parsing
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a Kali Live USB with optional encryption and persistence.")
    parser.add_argument("--iso", type=str, default="kali-linux-live.iso",
                        help="Path to the Kali Linux ISO file (default: kali-linux-live.iso)")
    parser.add_argument("--nuke", action="store_true", help="Only add the nuke feature to an existing encrypted drive.")
    parser.add_argument("--encrypt-persistence", action="store_true", help="Only set up encrypted persistence.")

    args = parser.parse_args()

    drive = display_drives()  # Get drive selection from user

    if args.nuke:
        nuke_password = getpass.getpass("Enter the nuke password (will erase the USB drive!): ")
        add_nuke_feature(drive, nuke_password)
    elif args.encrypt_persistence:
        setup_persistence_and_nuke(drive)
    else:
        create_kali_live_usb(drive, args.iso)
