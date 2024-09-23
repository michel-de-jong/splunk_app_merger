### DISCLAIMER
# USE THE SCRIPT AT YOUR OWN RISK
# ALWAYS VERIFY RESULTS

import os
import re
import sys
import shutil
import datetime

# import custom lib
sys.path.append(os.path.join(os.path.dirname(__file__), "lib"))

from script_logger import log_message

__name__ = "merger.py"
__author__ = "Michel de Jong"
logfile = "merger"

def merger(file_path, args):
    try:
        log_message(logfile, f"Processing apps: {file_path}", level="info")
        
    except PermissionError:
        print(f"ERROR: Permission denied: {file_path}")
    except Exception as e:
        log_message(logfile, f"Error processing {file_path}: {e}", level="error")
    
    # Calculate the runtime
        end_time = datetime.datetime.now()
        runtime = (end_time - start_time).seconds

        # Display the runtime notification
        print(f"Script completed in {runtime} seconds.")
        print(f"Logfiles are created in the working directory of the script")
        
        return