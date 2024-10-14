### DISCLAIMER
# USE THE SCRIPT AT YOUR OWN RISK
# ALWAYS VERIFY RESULTS

import os, sys
import shutil
import getpass
import subprocess
import datetime
import glob

# import custom lib
sys.path.append(os.path.join(os.path.dirname(__file__), "lib"))

from script_logger import log_message

__name__ = "merger.py"
__author__ = "Michel de Jong"
logfile = "merger"

def prompt_user_confirmation(prompt):
    """Prompt the user with a yes/no question and return True for 'yes', False for 'no'."""
    while True:
        answer = input(f"{prompt} (y/n): ").lower()
        if answer in ['y', 'n']:
            return answer == 'y'
        print("Invalid input. Please enter 'y' or 'n'.")

def prompt_user_choice(prompt, choices):
    """Prompt the user to choose between the given choices."""
    while True:
        choice = input(f"{prompt} \n").lower()
        if choice in choices:
            return choice
        print(f"Invalid input. Please choose from {choices}.")

def check_splunk_home():
    """
    Check if the SPLUNK_HOME environment variable is set and prompt the user to confirm.
    If not set or incorrect, ask the user to provide the correct path.
    """
    splunk_home = os.getenv('SPLUNK_HOME')
    while True:
        if splunk_home and prompt_user_confirmation(f"SPLUNK_HOME is set to {splunk_home}. Is this correct?"):
            print(f"Confirmed")
            pass
        else:
            splunk_home = input("Please provide the correct path for SPLUNK_HOME: ")

        if os.path.exists(splunk_home):
            log_message(logfile, f"SPLUNK_HOME set to {splunk_home}", level="info")
            return splunk_home
        else:
            raise FileNotFoundError(f"The provided SPLUNK_HOME path does not exist: {splunk_home}. Please try again.")

def get_dir(prompt_text):
    """Prompt the user for a directory path and ensure it exists."""
    while True:
        dir_path = input(prompt_text)
        
        if os.path.exists(dir_path):
            log_message(logfile, f"App directory set to {dir_path}", level="info")
            return dir_path
        else:
            print(f"The provided path does not exist: {dir_path}. Please try again.")

def get_credentials():
    """Prompt the user for Splunk login credentials."""
    while True:
        uname = input("Please provide your Splunk username: ")
        secret = getpass.getpass("Please provide your Splunk password: ")

        if uname and secret:
            log_message(logfile, f"Credentials received for user: {uname}", level="info")
            return uname, secret
        else:
            raise ValueError("Username and password cannot be empty. Please try again.")

def manage_content(splunk_home, relative_path):
    """
    Check if the specified directory contains any content.
    Prompt the user to either delete the content or back it up.
    """
    try:
        sp_path = os.path.join(splunk_home, relative_path)
        if not os.path.exists(sp_path) or not os.listdir(sp_path):
            log_message(logfile, f"No content found in {sp_path}.", level="info")
            return

        log_message(logfile, f"Directory {relative_path} contains content.", level="info")
        print(f"Directory {relative_path} contains content.")

        action = prompt_user_choice("Do you want to \n1) Delete or \n2) Backup the content?", ['1','2'])

        if action == '1':
            shutil.rmtree(sp_path)
            os.makedirs(sp_path)
            log_message(logfile, f"Content in {sp_path} deleted.", level="info")
            print(f"Content in {sp_path} has been deleted.")
            return
        
        elif action == '2':
            tmp_path = os.path.join(splunk_home, "tmp", relative_path.replace('/', "_"))
            os.makedirs(tmp_path, exist_ok=True)
            shutil.copytree(sp_path, tmp_path, dirs_exist_ok=True)
            shutil.rmtree(sp_path)
            os.makedirs(sp_path)
            log_message(logfile, f"Content in {sp_path} backed up to {tmp_path} and deleted", level="info")
            print(f"Content has been backed up to {tmp_path} and deleted from {sp_path}")
            return

    except Exception as e:
        log_message(logfile, f"Error managing content in {sp_path}: {e}", level="error")
        raise

def apply_shcluster_bundle(splunk_home, uname, secret):
    """
    Run the 'splunk apply shcluster-bundle' command with the provided credentials.
    This applies changes to the shcluster.
    """
    try:
        cmd = [
            os.path.join(splunk_home, "bin", "splunk"),
            "apply",
            "shcluster-bundle",
            "--answer-yes",
            "-action",
            "stage",
            "-auth",
            f"{uname}:{secret}"
        ]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        log_message(logfile, "Shcluster-bundle applied successfully", level="info")
        print("Shcluster-bundle applied successfully")
    except subprocess.CalledProcessError as e:
        log_message(logfile, f"Error applying shcluster-bundle: {e}", level="error")
        print(f"Error applying shcluster-bundle: {e}")
        raise

def remove_bundle_files(splunk_home):
    """
    Remove all files ending with *.bundle in $SPLUNK_HOME/var/run/splunk/deploy/apps.
    """
    try:
        apps_deploy_path = os.path.join(splunk_home, "var", "run", "splunk", "deploy", "apps")
        for file_name in glob.glob(os.path.join(apps_deploy_path, "*.bundle")):
            os.remove(file_name)
        log_message(logfile, "All *.bundle files removed from deploy/apps", level="info")
        print("All *.bundle files have been removed from deploy/apps")
    except Exception as e:
        log_message(logfile, f"Error removing *.bundle files: {e}", level="error")
        print(f"Error removing *.bundle files: {e}")
        raise

def copy_dir(src, dest):
    """
    Copy content from one directory to another.
    """
    try:
        if os.path.exists(dest):
            shutil.rmtree(dest)
            shutil.copytree(src, dest, dirs_exist_ok=True)
        log_message(logfile, f"Content copied from {src} to {dest}.", level="info")
    except Exception as e:
        log_message(logfile, f"Error copying content: {e}", level="error")
        print( f"Error copying content: {e}")
        raise

def merger():
    """
    Main function to manage the entire flow:
    - Check SPLUNK_HOME
    - Get app_dir and credentials
    - Manage content in shcluster and deploy directories
    - Copy apps, apply shcluster bundle, and handle backups
    """
    try:

        start_time = datetime.datetime.now()
        splunk_home = check_splunk_home()
        app_dir = get_dir("Please provide the path to the apps (app_dir) that need to be merged: ")
        uname, secret = get_credentials()

        # Manage content in shcluster/apps and deploy/apps
        manage_content(splunk_home, "etc/shcluster/apps")
        manage_content(splunk_home, "var/run/splunk/deploy/apps")

        # Copy apps to shcluster/apps
        copy_dir(app_dir, os.path.join(splunk_home, "etc", "shcluster", "apps"))

        # Apply the shcluster-bundle
        apply_shcluster_bundle(splunk_home, uname, secret)

        # Remove all *.bundle files
        remove_bundle_files(splunk_home)

        # Create apps_merged directory and copy remaining files
        apps_merged_dir = os.path.join(os.path.dirname(app_dir), "apps_merged")
        os.makedirs(apps_merged_dir, exist_ok=True)
        copy_dir(os.path.join(splunk_home, "var", "run", "splunk", "deploy", "apps"), apps_merged_dir)

        print(f"\nMerged apps can be found in {apps_merged_dir}\n")
        log_message(logfile, f"Merged apps can be found in {apps_merged_dir}", level="info")

        # Delete created content from shcluster/apps and deploy/apps
        shutil.rmtree(os.path.join(splunk_home, "etc", "shcluster", "apps"), ignore_errors=True)
        shutil.rmtree(os.path.join(splunk_home, "var", "run", "splunk", "deploy", "apps"), ignore_errors=True)

        # Calculate the runtime
        end_time = datetime.datetime.now()
        runtime = (end_time - start_time).seconds

        # Display the runtime notification
        print(f"Script completed in {runtime} seconds.")
        print(f"Logfiles are created in the working directory of the script")

    except Exception as e:
        log_message(logfile, f"An error occurred: {e}", level="error")
        print(f"An error occurred: {e}")
    
    return