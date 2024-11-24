import bz2
import os
from satpy import Scene
import matplotlib.pyplot as plt
import numpy as np

def decompress_bz2(file_path):
    """Decompress a bz2 file."""
    with bz2.BZ2File(file_path, 'rb') as file:
        decompressed_data = file.read()
    return decompressed_data

def calculate_brightness_temperature(data, band):
    """Convert raw satellite data to brightness temperature."""
    # Calibration constants for Himawari bands (adjust as necessary)
    K1 = 607.76 if band == 'B06' else 610.0  # Example constant for Band 6
    K2 = 1260.56 if band == 'B06' else 1260.0  # Example constant for Band 7
    brightness_temp = K2 / np.log((K1 / data) + 1) - 273.15  # Convert to Celsius
    return brightness_temp

def calculate_precipitable_water(band_6_temp, band_7_temp):
    """Estimate precipitable water vapor from brightness temperatures."""
    # Simplified formula for PWV estimation (adjust based on empirical data)
    pwv = (band_6_temp - band_7_temp) * 0.1  # Placeholder coefficient
    return pwv

def process_himawari_files(directory, band):
    """Process Himawari files to extract data for a specific band."""
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
    
    # Load the specified band
    scn.load([band])
    
    # Get the data array for the specified band
    band_data = scn[band].values
    
    return band_data

def main(b06_directory, b07_directory):
    """Main function to process Himawari data and calculate PWV."""
    # Process Band 6 and Band 7 files
    band_6_data = process_himawari_files(b06_directory, 'B06')
    band_7_data = process_himawari_files(b07_directory, 'B07')
    
    # Calculate brightness temperatures
    band_6_temp = calculate_brightness_temperature(band_6_data, 'B06')
    band_7_temp = calculate_brightness_temperature(band_7_data, 'B07')
    
    # Calculate precipitable water vapor
    pwv = calculate_precipitable_water(band_6_temp, band_7_temp)
    
    # Crop the image in the middle
    height, width = pwv.shape
    crop_size = min(height, width) // 4
    start_y = (height - 1 * crop_size) // 2
    start_x = (width - 3 * crop_size) // 2
    cropped_pwv = pwv[start_y:start_y + crop_size, start_x:start_x + crop_size]
    
    # Save the PWV image
    pwv_image_path = os.path.join(b06_directory, 'precipitable_water_vapor.png')
    plt.imsave(pwv_image_path, cropped_pwv, cmap='viridis')
    print(f'Precipitable water vapor image saved as {pwv_image_path}')

if __name__ == "__main__":
    # Specify the directories for Band 6 and Band 7
    b06_directory = './B06'  # Update this path as necessary
    b07_directory = './B07'  # Update this path as necessary

    # Run the main function
    main(b06_directory, b07_directory)
