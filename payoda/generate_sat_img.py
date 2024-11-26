import bz2
import os
import logging
from satpy import Scene
import matplotlib.pyplot as plt
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def decompress_bz2(file_path):
    """
    Decompress a .bz2 file.

    Args:
        file_path (str): The path to the .bz2 file.

    Returns:
        bytes: The decompressed data.
    """
    try:
        with bz2.BZ2File(file_path, 'rb') as file:
            decompressed_data = file.read()
        return decompressed_data
    except Exception as e:
        logging.error(f"Error decompressing file {file_path}: {e}")
        return None

def process_himawari_files(directory, output_filename='cropped_image.png', gamma=1.0, band='B13'):
    """
    Process Himawari files to generate a cropped image.

    Args:
        directory (str): The directory containing the downloaded .DAT.bz2 files.
        output_filename (str): The name of the output PNG file. Defaults to 'cropped_image.png'.
        gamma (float): The gamma correction factor. Defaults to 1.0.
        band (str): The band to process. Defaults to 'B13'.
    """
    # List all downloaded files in the directory
    files = [f for f in os.listdir(directory) if f.endswith('.DAT.bz2')]
    
    if not files:
        logging.warning("No .DAT.bz2 files found in the specified directory.")
        return

    # Decompress and save the data from each file
    decompressed_files = []
    for file in files:
        file_path = os.path.join(directory, file)
        decompressed_data = decompress_bz2(file_path)
        if decompressed_data is not None:
            decompressed_file_path = file_path.replace('.bz2', '')
            with open(decompressed_file_path, 'wb') as decompressed_file:
                decompressed_file.write(decompressed_data)
            decompressed_files.append(decompressed_file_path)
            logging.info(f"Decompressed and saved: {decompressed_file_path}")
        else:
            logging.error(f"Failed to decompress: {file_path}")

    if not decompressed_files:
        logging.warning("No files were successfully decompressed.")
        return

    # Use Satpy to read and process the decompressed files
    try:
        scn = Scene(filenames=decompressed_files, reader='ahi_hsd')
        scn.load([band])
        
        # Get the data array for the specified band
        data = scn[band].values
        
        # Crop the image in the middle
        height, width = data.shape
        crop_size = min(height, width) // 15
        start_y = (height - 2 * crop_size) // 2
        start_x = (width - 8 * crop_size) // 2
        cropped_data = data[start_y:start_y + crop_size, start_x:start_x + crop_size]
        
        # Apply gamma correction
        corrected_data = np.power(cropped_data, gamma)
        
        # Save the gamma-corrected cropped image
        #cropped_image_path = os.path.join(directory, output_filename)
        plt.imsave(output_filename, corrected_data, cmap='gray')
        logging.info(f'Cropped image saved as {output_filename}')
    
    except Exception as e:
        logging.error(f"Error processing files: {e}")
