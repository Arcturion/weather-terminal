from datetime import datetime, timedelta

def generate_recent_satellite_image(ftp_server, local_directory, output_directory, band='B13', resolution='20', gamma=0.05, username='dimascours_gmail.com', password='SP+wari8'):
    """


    Wrapper function to generate the most recent satellite image.

    Args:
        ftp_server (str): The FTP server address.
        local_directory (str): The local directory to save the raw files.
        output_directory (str): The directory to save the processed PNG images.
        band (str): The band to download and process. Defaults to 'B13'.
        resolution (str): The resolution to download. Defaults to '20'.
        username (str): FTP username. Defaults to 'dimascours_gmail.com'.
        password (str): FTP password. Defaults to 'SP+wari8'.
    """
    # Get the current UTC time
    current_time = datetime.utcnow()

    # Adjust the current time to the nearest previous 10-minute mark
    adjusted_time = current_time - timedelta(minutes=current_time.minute % 10, seconds=current_time.second, microseconds=current_time.microsecond)

    # Generate the output filename based on the adjusted time
    output_filename = adjusted_time.strftime('%Y%m%d_%H%M.png')
    output_file_path = os.path.join(output_directory, output_filename)

    # Check if the output file already exists
    if os.path.exists(output_file_path):
        logging.info(f"Recent image already exists: {output_file_path}")
        return

    # If the image does not exist, download the raw data
    logging.info("Recent image not found. Downloading raw data...")
    download_himawari_hsd_files(ftp_server, local_directory, adjusted_time, band, resolution)

    # Process the downloaded files
    process_himawari_files(local_directory, output_filename=output_file_path, gamma=gamma, band=band)

    # Clean up: delete the raw data files
    for file in os.listdir(local_directory):
        if file.endswith('.DAT') or file.endswith('.DAT.bz2'):
            os.remove(os.path.join(local_directory, file))
            logging.info(f"Deleted raw data file: {file}")



if __name__ == "__main__":
    ftp_server = 'ftp.ptree.jaxa.jp'
    local_directory = './himawari_data'  # Directory to store raw data
    output_directory = './sat'  # Directory to save processed images

    while True:
        try:
            generate_recent_satellite_image(ftp_server, local_directory, output_directory, band='B13', resolution='20', gamma=4)
            # Sleep for 10 minutes before checking again
            time.sleep(30)  # 600 seconds = 10 minutes
        except Exception as e:
            logging.error(f"An error occurred: {e}")
            # Optional: Sleep for a shorter time before retrying in case of an error
            time.sleep(30)  # 60 seconds = 1 minute
