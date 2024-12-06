import os
import sys
import yaml
from src.config_loader import load_yaml_config
from src.ocr_engine import OCREngine
from src.box_merger import post_process
from src.image_redactor import apply_vendor_specific_zones
from PIL import Image

def process_ultrasound_scans(input_directory_str, output_directory_str, valid_annotation_keywords_dict, vendor_specific_zones_dict):
    """
    Main program callpoint.
    Processes all image files in a given directory, and saves the results to a YAML file.
    """
    
    # Initialize the OCR engine once
    engine = OCREngine()

    # Iterate over all files inside the input directory, and process them if they are images
    ocr_results = {}
    for filename in os.listdir(input_directory_str):
        if filename.lower().endswith((".png", ".jpg", ".jpeg", ".tiff", ".gif")):            
            print(f"Processing image: {filename}")

            # 1) Black out unneeded regions of the image
            with Image.open(os.path.join(input_directory_str, filename)) as image:
                simplified_image = apply_vendor_specific_zones(image, input_directory_str, vendor_specific_zones_dict)

            # 2) Pass image through the OCR engine
            result = engine.run_ocr(simplified_image)
            
            # 3) Clean up artifacts and spellcheck detected words
            post_processed_result = post_process(result, valid_annotation_keywords_dict)

            # 4) Store result in readable format
            ocr_results[filename] = [line[1][0] for line in post_processed_result]

    # Save all the results
    output_file_path = os.path.join(output_directory_str, "ocr_results.yaml")
    with open(output_file_path, "w") as output_file:
        yaml.dump(ocr_results, output_file, default_flow_style=False)
        print(f"OCR results written to {output_file_path}")

if __name__ == "__main__":
    """
    Example command line driver.
    """

    if len(sys.argv) != 5:
        # Incorrect number of arguments
        print("Usage: python main.py <input_directory> <output_directory> <valid_annotation_keywords.yaml> <vendor_inclusion_zones.yaml>")
        sys.exit(1)

    input_directory = sys.argv[1]
    output_directory = sys.argv[2]
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    valid_annotation_keywords = load_yaml_config(sys.argv[3])
    vendor_inclusion_zones = load_yaml_config(sys.argv[4])

    process_ultrasound_scans(input_directory, output_directory, valid_annotation_keywords, vendor_inclusion_zones)
