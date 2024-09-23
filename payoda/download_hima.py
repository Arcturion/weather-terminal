import ftplib
import os
from datetime import datetime, timedelta
import re

def download_himawari_hsd_files(ftp_server, local_directory, username='#', password='#'):
    # Determine the current time in UTC
    now = datetime.utcnow()
    year_month = now.strftime('%Y%m')
    day = now.strftime('%d')
    hour = now.strftime('%H')
    
    # Construct the FTP directory path
    ftp_directory = f'jma/hsd/{year_month}/{day}/{hour}'
    
    # Connect to the FTP server
    ftp = ftplib.FTP(ftp_server)
    ftp.login(user=username, passwd=password)
    
    # Change to the specified directory
    ftp.cwd(ftp_directory)
    
    # List files in the directory with their modification times
    files = []
    ftp.retrlines('MLSD', files.append)
    
    # Define the pattern to match the desired files
    pattern = re.compile(r'^HS_H09_\d{8}_(\d{4})_B03_FLDK_R05_S(0[1-9]\d{2}|10[01]\d)\.DAT\.bz2$')
    
    # Find all files matching the pattern
    matching_files = {}
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
    
    # Ensure the local directory exists
    if not os.path.exists(local_directory):
        os.makedirs(local_directory)
    
    # Download the matching file nearest to the current time
    if matching_files:
        # Find the time key nearest to the current time
        nearest_time_key = min(matching_files.keys(), key=lambda k: abs(datetime.strptime(k, '%H%M') - now))
        for file, _ in matching_files[nearest_time_key]:
            local_file_path = os.path.join(local_directory, file)
            with open(local_file_path, 'wb') as local_file:
                ftp.retrbinary(f'RETR {file}', local_file.write)
                print(f'Downloaded: {file}')
    else:
        print("No matching files found in the directory.")
    
    # Close the FTP connection
    ftp.quit()

# Example usage
ftp_server = 'ftp.ptree.jaxa.jp'  # Replace with the actual FTP server
local_directory = '.'  # Local directory to save the file

download_himawari_hsd_files(ftp_server, local_directory)
