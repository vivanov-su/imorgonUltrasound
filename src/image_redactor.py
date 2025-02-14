import os
import numpy as np
from PIL import Image

def apply_vendor_specific_zones(image_PIL, input_directory_str, vendor_inclusion_zones_dict, ocr_settings_dict):
    
    # Use folder name for the corresponding vendor
    folder_name = os.path.basename(os.path.normpath(input_directory_str))
    specific_vendor = vendor_inclusion_zones_dict.get(folder_name, None)

    # Check if vendor's inclusion zone data is available
    if not specific_vendor:
        print(f"WARNING: Vendor name '{folder_name}' not found. Scanning the whole image.")
        inclusion_zones = []  # Default to scanning the entire image
    
    else:
        # Convert the image to numpy array and get image dimensions
        image_np = np.array(image_PIL)
        image_width, image_height = image_PIL.size

        # Match the image size with the ones in the inclusion zones data
        matched_zones = next(
            (item for item in specific_vendor if item["image_size"] == [image_width, image_height]), None
        )

        if matched_zones:
            inclusion_zones = matched_zones["boxes"]
        else:
            print(f"INFO: No matching resolution found for image in vendor '{folder_name}'. Scanning the whole image.")
            inclusion_zones = []  # Default to scanning the entire image

    # If inclusion zones are enabled and exist for this vendor, copy over the parts of the original image that are inside
    if ocr_settings_dict.get("use_inclusion_zones", False) and inclusion_zones:
        masked_image_np = np.zeros_like(image_np)
        for (x1, y1, x2, y2) in inclusion_zones:
            masked_image_np[y1:y2, x1:x2] = image_np[y1:y2, x1:x2]
    else:
        masked_image_np = image_np  # No zones provided; copy over the entire original image

    # Return masked image
    return Image.fromarray(masked_image_np)
