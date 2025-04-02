# update apt
# install deps
# clone wallpapers
# copy config
# copy fonts
# themes
import logging
import subprocess

# Setup logging configuration
logging.basicConfig(
    level=logging.INFO,  # Define the log level
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("dotfile.log"),  # Log messages will be saved to this file
        logging.StreamHandler()  # Log messages will also appear in the standard output
    ]
)

def check_kernel_update():
    """
    Check if there is an update available for the Linux kernel on a Debian/Ubuntu system.
    """
    try:
        # Run 'apt list --upgradable' to list all upgradable packages
        logging.info("Checking for kernel updates...")
        result = subprocess.run(
            ["apt", "list", "--upgradable"],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True
        )

        # Kernel packages typically include "linux-image" or "linux-headers" in their names
        upgradable_packages = result.stdout
        kernel_updates = [
            line for line in upgradable_packages.splitlines()
            if "linux-image" in line or "linux-headers" in line
        ]

        if kernel_updates:
            logging.info("Kernel updates are available:")
            for update in kernel_updates:
                logging.info(f"  - {update}")
        else:
            logging.info("No kernel updates are available.")

    except subprocess.CalledProcessError as e:
        logging.error(f"An error occurred while checking for updates: {e}")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")

def update_system():
    """
    Updates the Debian/Ubuntu system.
    """
    try:
        # Update the package list
        logging.info("Updating package list...")
        subprocess.run(["sudo", "apt", "update"], check=True)

        # Upgrade installed packages
        logging.info("Upgrading installed packages...")
        subprocess.run(["sudo", "apt", "upgrade", "-y"], check=True)

        # Remove unnecessary packages
        logging.info("Removing unnecessary packages...")
        subprocess.run(["sudo", "apt", "autoremove", "-y"], check=True)
        subprocess.run(["sudo", "apt", "autoclean"], check=True)

        logging.info("System update completed successfully.")
    except subprocess.CalledProcessError as e:
        logging.error(f"An error occurred during the update: {e}")


check_kernel_update()
update_system()
