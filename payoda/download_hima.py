import ftplib
import os
import logging
from datetime import datetime
import re
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def download_himawari_hsd_files(ftp_server, local_directory, target_time=None, band='B13', resolution='20', username='#', password='#'):
    """
    Download Himawari HSD files from the FTP server for a specific time.

    Args:
        ftp_server (str): The FTP server address.
        local_directory (str): The local directory to save the files.
        target_time (datetime, optional): The target UTC time for file retrieval. Defaults to now.
        band (str, optional): The band to download. Defaults to 'B13'.
        resolution (str, optional): The resolution to download. Defaults to '20'.
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

    while True:
        try:
            # Connect to the FTP server
            ftp = ftplib.FTP(ftp_server)
            ftp.login(user=username, passwd=password)

            # Navigate to the specified directory
            ftp_directory = f'jma/hsd/{year_month}/{day}/{hour}'
            logging.info(f"Navigating to directory: {ftp_directory}")
            ftp.cwd(ftp_directory)

            # Regex to match specific file patterns based on target time
            file_time_pattern = target_time.strftime('%H%M')
            pattern = re.compile(
                rf'^HS_H09_\d{{8}}_{file_time_pattern}_{band}_FLDK_R{resolution}_S(0[1-9]\d{{2}}|10[01]\d)\.DAT\.bz2$'
            )

            # Retrieve the list of files and filter using the pattern
            files = []
            ftp.retrlines('NLST', files.append)  # Use 'NLST' for a simpler file list
            matching_files = [file for file in files if pattern.match(file)]

            if not matching_files:
                logging.warning(f"No matching files found for time {file_time_pattern}. Waiting for 1 minute before retrying...")
                time.sleep(60)  # Wait for 1 minute before retrying
                continue  # Retry the loop

            if len(matching_files) < 10:
                logging.warning(f"Found {len(matching_files)} matching files, which is less than 10. Waiting for 1 minute before retrying...")
                time.sleep(60)  # Wait for 1 minute before retrying
                continue  # Retry the loop

            logging.info(f"Found {len(matching_files)} matching files. Starting download...")
            print(f"Found {len(matching_files)} matching filesfor time {file_time_pattern}. Starting download...")

            # Download each matching file
            for file in matching_files:
                local_file_path = os.path.join(local_directory, file)
                with open(local_file_path, 'wb') as local_file:
                    ftp.retrbinary(f'RETR {file}', local_file.write)
                    logging.info(f"Downloaded: {file}")
                    print(f"Downloaded: {file}")

            break  # Exit the loop after successful download

        except ftplib.error_perm as e:
            logging.error(f"FTP error: {e}")
            break  # Exit the loop on FTP error
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")
            break  # Exit the loop on unexpected error
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
target_time = datetime(2024, 11, 26, 11, 10)  # UTC time with minutes
'''
