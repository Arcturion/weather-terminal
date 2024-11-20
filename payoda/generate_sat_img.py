import bz2
import os
from satpy import Scene
from glob import glob
import matplotlib.pyplot as plt
import numpy as np

def decompress_bz2(file_path):
    with bz2.BZ2File(file_path, 'rb') as file:
        decompressed_data = file.read()
    return decompressed_data

def process_himawari_files(directory, gamma=1.0, band='B13'):
    # List all downloaded files in the directory
    files = [f for f in os.listdir(directory) if f.endswith('.DAT.bz2')]
    
    # Decompress and save the data from each file
    decompressed_files = []
    for file in files:
        file_path = os.path.join(directory, file)
        decompressed_data = decompress_bz2(file_path)
        decompressed_file_path = file_path.replace('.bz2', '')
        with open(decompressed_file_path, 'wb') as decompressed_file:
            decompressed_file.write(decompressed_data)
        decompressed_files.append(decompressed_file_path)
    
    # Use Satpy to read and process the decompressed files
    scn = Scene(filenames=decompressed_files, reader='ahi_hsd')
    scn.load([band])
    
    # Get the data array for B03
    data = scn[band].values
    
    # Crop the image in the middle
    height, width = data.shape
    crop_size = min(height, width) // 15
    start_y = (height - 2*crop_size) // 2
    start_x = (width - 8*crop_size) // 2
    cropped_data = data[start_y:start_y+crop_size, start_x:start_x+crop_size]
    
    # Apply gamma correction
    corrected_data = np.power(cropped_data, gamma)
    
    # Save the gamma-corrected cropped image
    cropped_image_path = os.path.join(directory, 'cropped_image.png')
    plt.imsave(cropped_image_path, corrected_data, cmap='gray')
    print(f'Cropped image saved as {cropped_image_path}')

# Example usage
directory = '.'  # Directory where the downloaded files are stored
process_himawari_files(directory, gamma=0.05)
