import os
import sys
import yaml
from src.config_loader import load_yaml_config
from src.ocr_engine import OCREngine
from src.box_merger import post_process
from src.image_redactor import apply_vendor_specific_zones
from PIL import Image

def process_ultrasound_scans(input_directory_str, valid_annotation_keywords_dict, vendor_specific_zones_dict, ocr_settings_dict):
    """
    Main program callpoint.
    Processes all image files in a given directory, and saves the results to a YAML file.
    """
    
    # Initialize the OCR engine with the settings
    engine = OCREngine(ocr_settings_dict)

    # Iterate over all files inside the input directory and process them if they are images
    directory_result = {}
    for filename in os.listdir(input_directory_str):
        if filename.lower().endswith((".png", ".jpg", ".jpeg", ".tiff", ".gif")):            
            print(f"Processing image: {filename}")

            # 1) Black out unneeded regions of the image
            with Image.open(os.path.join(input_directory_str, filename)) as image:
                simplified_image = apply_vendor_specific_zones(image, input_directory_str, vendor_specific_zones_dict, ocr_settings_dict)

            # 2) Pass image through the OCR engine
            results = engine.run_ocr(simplified_image)

            # 3) Clean up artifacts, spellcheck detected words, and format the OCR data 
            clean_results = post_process(results, valid_annotation_keywords_dict, ocr_settings_dict)

            # 4) Attach the results to the file's name
            directory_result[filename] = clean_results

    return directory_result

if __name__ == "__main__":
    """
    Example command line driver.
    """

    if len(sys.argv) != 3:
        # Incorrect number of arguments
        print("Usage: python main.py <input_directory> <output_directory>")
        sys.exit(1)

    input_directory = sys.argv[1]
    output_directory = sys.argv[2]
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Load required config files
    valid_annotation_keywords = load_yaml_config("valid_annotation_keywords.yaml")
    vendor_inclusion_zones = load_yaml_config("vendor_inclusion_zones.yaml")
    ocr_settings = load_yaml_config("ocr_settings.yaml")

    # Run the extraction program. Returns a dictionary of filenames to a list of their keywords 
    ocr_results = process_ultrasound_scans(input_directory, valid_annotation_keywords, vendor_inclusion_zones, ocr_settings)
    
    # Save output to file
    output_file_path = os.path.join(output_directory, "ocr_results.yaml")
    with open(output_file_path, "w") as output_file:
        yaml.dump(ocr_results, output_file, default_flow_style=False)
        print(f"### OCR results written to {output_file_path}")
