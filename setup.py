# update apt
# install deps
# clone wallpapers
# copy config
# copy fonts
# themes
import logging
import subprocess
from colorama import Fore, Style, init

# Initialize Colorama
init(autoreset=True)


class ColorizedFormatter(logging.Formatter):
    """
    Custom log formatter to add colors for console output.
    """
    COLORS = {
        logging.DEBUG: Fore.BLUE,  # Blue for debug messages
        logging.INFO: Fore.GREEN,  # Green for informational messages
        logging.WARNING: Fore.YELLOW,  # Yellow for warnings
        logging.ERROR: Fore.RED,  # Red for errors
        logging.CRITICAL: Fore.MAGENTA  # Magenta for critical errors
    }

    def format(self, record):
        color = self.COLORS.get(record.levelno, "")
        message = super().format(record)
        return f"{color}{message}{Style.RESET_ALL}"

# Setup logging
file_handler = logging.FileHandler("kernel_update.log")  # Log to file
console_handler = logging.StreamHandler()  # Log to console

# Colors only for console
console_formatter = ColorizedFormatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(console_formatter)

# Standard (non-color) formatter for file
file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(file_formatter)

# Configure global logger
logging.basicConfig(level=logging.INFO, handlers=[file_handler, console_handler])


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
            logging.warning("Kernel updates are available:")
            for update in kernel_updates:
                logging.info(f"  - {update}")
            logging.warning("Please update the kernel and reboot before continuing.")
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

def main():
    """
    Main function to execute the kernel update check.
    """
    # Perform the kernel update check
    check_kernel_update()
    # Configure the logging system
    update_system()

# Entry point of the script
if __name__ == "__main__":
    main()
