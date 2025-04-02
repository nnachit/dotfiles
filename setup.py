import logging
import os
import shutil
import subprocess
from colorama import Fore, Style, init
from git import Repo, GitCommandError

# Initialize Colorama
init(autoreset=True)


REQUIREMENT_FILE = "system-requirements.txt"
WAllPAPER_REPO = "https://github.com/harilvfs/wallpapers"
PICTURE_DIR = "~/Images/"
P10K_REPO = "https://github.com/romkatv/powerlevel10k.git"
P10K_DIR = "~/.config/"
P10K_TARGET = "powerlevel10k"
FONTS_DIR = "fonts"
FONTS_TARGET = "~/.fonts"
THEMES_DIR = "themes"
THEMES_TARGET = "~/.themes"


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


def install_system_requirements():

    with open(REQUIREMENT_FILE, "r") as f:
        packages = [package.strip() for package in f if package.strip() and not package.startswith("#")]

    if packages:
        cmd = ["sudo", "apt", "install", "-y"] + packages
        logging.info(f"Installing packages : {', '.join(packages)}")
        subprocess.run(cmd)
    else:
        logging.info("No packages to install.")


def copy_config(source_dir="config", destination_dir="~/.config"):

    destination_dir = os.path.expanduser(destination_dir)

    try:
        # Ensure the source directory exists
        if not os.path.exists(source_dir):
            logging.error(f"Source directory '{source_dir}' does not exist.")
            return

        # Ensure the destination directory exists, create it if necessary
        if not os.path.exists(destination_dir):
            logging.info(f"Destination directory '{destination_dir}' does not exist. Creating it...")
            os.makedirs(destination_dir, exist_ok=True)

        # Iterate through all files and subdirectories in the source directory
        for item in os.listdir(source_dir):
            source_path = os.path.join(source_dir, item)
            destination_path = os.path.join(destination_dir, item)

            # Copy files or directories
            if os.path.isdir(source_path):
                # If it's a directory, copy recursively
                if os.path.exists(destination_path):
                    logging.warning(f"Directory already exists: {destination_path}. Skipping...")
                else:
                    logging.info(f"Copying directory '{source_path}' to '{destination_path}'...")
                    shutil.copytree(source_path, destination_path)
            else:
                # For files, overwrite if they already exist
                logging.info(f"Copying file '{source_path}' to '{destination_path}'...")
                shutil.copy2(source_path, destination_path)

        logging.info(f"Contents of '{source_dir}' successfully copied to '{destination_dir}'.")

    except Exception as e:
        logging.error(f"An error occurred during copying: {e}")


def clone_repo(repo_url, picture_dir, target_subdir=""):
    """
    Clone a Git repository into a subdirectory of the folder specified by PICTURE_DIR.

    :param repo_url: The URL of the Git repository to clone.
    :param picture_dir: The base directory where the repo should be cloned (e.g. PICTURE_DIR).
    :param target_subdir: The name of the subfolder where the repo should be cloned.
    """
    picture_dir = os.path.expanduser(picture_dir)
    try:
        # Ensure the PICTURE_DIR exists
        if not os.path.isdir(picture_dir):
            logging.info(f"The directory {picture_dir} does not exist. Creating it...")
            os.makedirs(picture_dir, exist_ok=True)

        # Define the full path to the target folder
        target_path = os.path.join(picture_dir, target_subdir)

        # Check if the repository is already cloned
        if os.path.exists(target_path):
            logging.warning(f"The directory '{target_path}' already exists. Skipping clone...")
            return

        # Clone the git repo
        logging.info(f"Cloning repository '{repo_url}' into '{target_path}'...")
        Repo.clone_from(repo_url, target_path)
        logging.info("Repository successfully cloned.")

    except GitCommandError as e:
        logging.error(f"An error occurred while running Git commands: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")

def install_p10k():
    # echo 'source ~/powerlevel10k/powerlevel10k.zsh-theme' >>~/.zshrc
    pass

def main():
    check_kernel_update()
    update_system()
    install_system_requirements()
    # clone wallpapers
    clone_repo(WAllPAPER_REPO, PICTURE_DIR, "wallpapers")
    # Install p10k
    clone_repo(P10K_REPO, P10K_DIR, P10K_TARGET)
    # Install fonts
    copy_config(FONTS_DIR, FONTS_TARGET)
    copy_config(THEMES_DIR, THEMES_TARGET)

# Entry point of the script
if __name__ == "__main__":
    main()
