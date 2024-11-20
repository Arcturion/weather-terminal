import ftplib
import os
import logging
from datetime import datetime
import re

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def download_himawari_hsd_files(ftp_server, local_directory, target_time=None, band='B03', username='dimascours_gmail.com', password='SP+wari8'):
    """
    Download Himawari HSD files from the FTP server for a specific time.

    Args:
        ftp_server (str): The FTP server address.
        local_directory (str): The local directory to save the files.
        target_time (datetime, optional): The target UTC time for file retrieval. Defaults to now.
        username (str, optional): FTP username. Defaults to '#'.
        password (str, optional): FTP password. Defaults to '#'.
    """
    # Set the target time to now if not provided
    if target_time is None:
        target_time = datetime.utcnow()

    # Extract year, month, day, hour, and minute from target_time
    year_month = target_time.strftime('%Y%m')
    day = target_time.strftime('%d')
    hour = target_time.strftime('%H')
    minute = target_time.strftime('%M')

    # Ensure the local directory exists
    os.makedirs(local_directory, exist_ok=True)

    try:
        # Connect to the FTP server
        ftp = ftplib.FTP(ftp_server)
        ftp.login(user=username, passwd=password)

        # Navigate to the specified directory
        ftp_directory = f'jma/hsd/{year_month}/{day}/{hour}'
        logging.info(f"Navigating to directory: {ftp_directory}")
        ftp.cwd(ftp_directory)

        # Regex to match specific file patterns based on target time
        # File names include the 4-digit minute in HHMM format
        file_time_pattern = target_time.strftime('%H%M')
        pattern = re.compile(
            rf'^HS_H09_\d{{8}}_{file_time_pattern}_{band}_FLDK_R05_S(0[1-9]\d{{2}}|10[01]\d)\.DAT\.bz2$'
        )

        # Retrieve the list of files and filter using the pattern
        files = []
        ftp.retrlines('NLST', files.append)  # Use 'NLST' for a simpler file list
        matching_files = [file for file in files if pattern.match(file)]

        if matching_files:
            logging.info(f"Found {len(matching_files)} matching files. Starting download...")
        else:
            logging.warning(f"No matching files found for time {file_time_pattern}.")
            return

        # Download each matching file
        for file in matching_files:
            local_file_path = os.path.join(local_directory, file)
            with open(local_file_path, 'wb') as local_file:
                ftp.retrbinary(f'RETR {file}', local_file.write)
                logging.info(f"Downloaded: {file}")

    except ftplib.error_perm as e:
        logging.error(f"FTP error: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
    finally:
        # Ensure the FTP connection is closed
        try:
            ftp.quit()
            logging.info("FTP connection closed.")
        except:
            pass


'''
# Example usage:
ftp_server = 'ftp.ptree.jaxa.jp'
local_directory = './himawari_data'
# Example with a specific time
target_time = datetime(2024, 11, 19, 7, 20)  # UTC time with minutes
download_himawari_hsd_files(ftp_server, local_directory, target_time)
'''
