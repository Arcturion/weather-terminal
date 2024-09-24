import ftplib
import os
import time
from datetime import datetime, timedelta
import re

# Set the local directory with yearmonthday format
now = datetime.utcnow()
year_month_day = now.strftime('%Y%m%d')
local_directory = os.path.join('.', year_month_day)

# Ensure the local directory exists
if not os.path.exists(local_directory):
    os.makedirs(local_directory)

def download_himawari_hsd_files(ftp_server, local_directory, username='dimascours_gmail.com', password='SP+wari8'):
    # Determine the current time in UTC
    year_month = now.strftime('%Y%m')
    day = now.strftime('%d')
    hour = now.strftime('%H')
    
    # Function to change to the FTP directory and handle 550 errors
    def change_to_ftp_directory(ftp, year_month, day, hour):
        ftp_directory = f'jma/hsd/{year_month}/{day}/{hour}'
        try:
            ftp.cwd(ftp_directory)
            return True
        except ftplib.error_perm as e:
            if "550" in str(e):
                print(f"Directory {ftp_directory} not found. Checking previous hour...")
                previous_hour = str(int(hour) - 1).zfill(2)
                previous_directory = f'jma/hsd/{year_month}/{day}/{previous_hour}'
                try:
                    ftp.cwd(previous_directory)
                    print(f"Changed to previous directory: {previous_directory}")
                    return True
                except ftplib.error_perm as e:
                    print(f"Directory {previous_directory} not found either. Exiting...")
                    return False
            else:
                raise e  # Raise other FTP errors
        return True

    # Connect to the FTP server
    ftp = ftplib.FTP(ftp_server)
    ftp.login(user=username, passwd=password)
    
    # Change to the specified directory
    if not change_to_ftp_directory(ftp, year_month, day, hour):
        return

    pattern = re.compile(r'^HS_H09_\d{8}_(\d{4})_B03_FLDK_R05_S(0[1-9]\d{2}|10[01]\d)\.DAT\.bz2$')
    
    # Keep trying until we get 10 matching files
    matching_files = {}
    while True:
        files = []
        ftp.retrlines('MLSD', files.append)  # List files
        
        # Reset matching_files for each retry
        matching_files = {}
        
        # Find all files matching the pattern
        for entry in files:
            facts = dict(item.split('=') for item in entry.split(';') if '=' in item)
            file = entry.split(';')[-1].strip()
            match = pattern.match(file)
            if match:
                time_key = match.group(1)  # Extract the 4-digit time key (HHMM)
                file_time = datetime.strptime(facts["modify"], "%Y%m%d%H%M%S")
                if time_key not in matching_files:
                    matching_files[time_key] = []
                matching_files[time_key].append((file, file_time))
        
        # Check if we have 10 matching files for the nearest time key
        if matching_files:
            nearest_time_key = min(matching_files.keys(), key=lambda k: abs(datetime.strptime(k, '%H%M') - now))
            if len(matching_files[nearest_time_key]) == 10:
                print(f"Found 10 files for time key {nearest_time_key}. Proceeding to check for existing files...")
                
                # Check for already downloaded files
                downloaded_files = set(os.listdir(local_directory))
                files_to_download = []
                
                for file, _ in matching_files[nearest_time_key]:
                    if file in downloaded_files:
                        print(f"File {file} already downloaded. Skipping...")
                    else:
                        files_to_download.append(file)
                
                if files_to_download:
                    print(f"{len(files_to_download)} files need to be downloaded.")
                    break
                else:
                    print(f"All files for time key {nearest_time_key} have already been downloaded. Exiting.")
                    return
            else:
                print(f"Found {len(matching_files[nearest_time_key])} files, waiting for 60 seconds...")
        else:
            print("No matching files found, waiting for 60 seconds...")
        
        # Wait for 30 seconds before trying again
        time.sleep(60)
    
    # Download the files that have not been downloaded
    for file in files_to_download:
        local_file_path = os.path.join(local_directory, file)
        with open(local_file_path, 'wb') as local_file:
            ftp.retrbinary(f'RETR {file}', local_file.write)
            print(f'Downloaded: {file}')
    
    # Close the FTP connection
    ftp.quit()

# Example usage
ftp_server = 'ftp.ptree.jaxa.jp'  # Replace with the actual FTP server

download_himawari_hsd_files(ftp_server, local_directory)
