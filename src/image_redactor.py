import os
import numpy as np
from PIL import Image

def apply_vendor_specific_zones(image_PIL, input_directory_str, vendor_inclusion_zones_dict, ocr_settings_dict):    
    
    # Use folder name for the corresponding vendor
    folder_name = os.path.basename(os.path.normpath(input_directory_str))
    inclusion_zones = vendor_inclusion_zones_dict.get(folder_name, None)
    
    # Check if vendor name is not found in the dictionary
    if inclusion_zones is None:
        print(f"WARNING: Vendor name '{folder_name}' not found. Scanning the whole image.")
        inclusion_zones = []  # Default to an empty list so no masking occurs
        
    # Convert image to numpy array
    image_np = np.array(image_PIL)
    included_image_np = np.zeros_like(image_np)
    
    # If inclusion zones exist and are enabled, copy over the original pixels into them; otherwise use the whole image
    if inclusion_zones and ocr_settings_dict.get("use_inclusion_zones", False):
        for (x1, y1, x2, y2) in inclusion_zones:
            included_image_np[y1:y2, x1:x2] = image_np[y1:y2, x1:x2]
    else:
        included_image_np = image_np  # No zones provided; retain use full image
    
    # Return processed image
    return Image.fromarray(included_image_np)
