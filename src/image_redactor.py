import os
import numpy as np
from PIL import Image

def apply_vendor_specific_zones(image_PIL, input_directory_str, vendor_specific_zones_dict):    
    # Use folder name for the corresponding vendor
    folder_name = os.path.basename(os.path.normpath(input_directory_str))
    bounding_boxes = vendor_specific_zones_dict.get(folder_name, [])
    
    # Black out all pixels outside of the bounding boxes
    image_np = np.array(image_PIL)
    masked_image_np = np.zeros_like(image_np)
    for (x1, y1, x2, y2) in bounding_boxes:
        masked_image_np[y1:y2, x1:x2] = image_np[y1:y2, x1:x2]

    return Image.fromarray(masked_image_np)
