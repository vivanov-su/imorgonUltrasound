import os
import sys
import yaml
from src.config_loader import load_yaml_config
from src.ocr_engine import OCREngine

def process_directory(engine, directory_path, output_directory, settings, vendor_exclusion_zones):
    """
    Processes all image files in a given directory using an OCR engine and saves the results to a YAML file.

    Args:
        engine (OCREngine): The instance of the OCR engine used for processing images.
        directory_path (str): The path to the directory containing image files to process.
        output_directory (str): The path to the directory where the results file will be saved.
        settings (dict): Configuration settings for the OCR engine.
        vendor_exclusion_zones (dict): Zones to exclude from OCR processing, as specified by the vendor.

    Returns:
        None
    """
    
    # Dictionary to store OCR results for each image
    ocr_results = {}

    # Iterate over all files in the given directory
    for filename in os.listdir(directory_path):
        image_path = os.path.join(directory_path, filename)

        # Check if the file is an image based on its extension
        if filename.lower().endswith((".png", ".jpg", ".jpeg", ".tiff", ".gif")):
            print(f"Processing {filename}")
            ocr_results[filename] = engine.process_image(image_path, vendor_exclusion_zones, settings)

    # Define output file location
    output_file_path = os.path.join(output_directory, "ocr_results.yaml")
    
    # Write OCR results to a YAML file
    with open(output_file_path, "w") as yaml_file:
        yaml.dump(ocr_results, yaml_file, default_flow_style=False)

    print(f"OCR results written to {output_file_path}")

if __name__ == "__main__":
    """Main program entrypoint.

    Called by application.
    """
        
    # Check if the correct number of command-line arguments is provided
    if len(sys.argv) != 5:
        print("Usage: python main.py <image_directory> <output_directory> <settings.yaml> <vendor_exclusion_zones.yaml>")
        sys.exit(1)

    # Get the input directory containing images and output directory location from command-line arguments
    directory_path = sys.argv[1]
    output_directory = sys.argv[2]

    # Check and create output directory if it doesn't exist
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Load settings and vendor exclusion zones from YAML files
    settings_file = sys.argv[3]
    settings = load_yaml_config(settings_file)
    vendor_exclusion_zones_file = sys.argv[4]
    vendor_exclusion_zones = load_yaml_config(vendor_exclusion_zones_file)

    # Initialize the OCR engine once for global use
    engine = OCREngine()

    process_directory(engine, directory_path, output_directory, settings, vendor_exclusion_zones)
