### DISCLAIMER
# USE THE SCRIPT AT YOUR OWN RISK
# ALWAYS VERIFY RESULTS

import sys
import os
import argparse

# import custom lib
sys.path.append(os.path.join(os.path.dirname(__file__), "lib"))

from module_checker import check_modules

__name__ = "splunk_app_merger.py"
__author__ = "Michel de Jong"

def splunk_app_merger():
    try:
        # Check if the required modules are available
        required_modules = ['shutil', 'datetime', 'subprocess', 'glob', 'getpass', 'os', 'sys']
        check_modules(required_modules)

        # Merge configs
        from merger import merger
        merger()

        print("Finished. Exiting the script")
        exit(0)

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "splunk_app_merger.py":
    parser = argparse.ArgumentParser(description="Python script to merge app/local + app/metadata/local.meta to app/default + app/metadata/default.meta. Local Splunk Enterprise installation is required. Please refer the README.md for more information.")
    splunk_app_merger()