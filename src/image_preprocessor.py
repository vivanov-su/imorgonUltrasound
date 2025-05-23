import os
import numpy as np
from PIL import Image
import cv2

def make_black_and_white(image, ocr_settings_dict):
    if not ocr_settings_dict.get("black_and_white", False):
        return image
    
    # Convert PIL image to grayscale numpy array
    image_gray = image.convert("L")  # "L" for (8-bit pixels, black and white)
    image_np = np.array(image_gray)

    threshold = ocr_settings_dict.get("binarization_threshold", 155)
    _, binarized_np = cv2.threshold(image_np, threshold, 255, cv2.THRESH_BINARY)

    # Convert back to PIL image
    bw_image = Image.fromarray(binarized_np)
    return bw_image

def increase_contrast(image, ocr_settings_dict):
    if not ocr_settings_dict.get("increase_image_contrast", False):
        return image
    
    # Convert PIL to numpy BGR for OpenCV
    image_np = np.array(image)
    # Handle grayscale input
    if len(image_np.shape) == 2:
        image_np = cv2.cvtColor(image_np, cv2.COLOR_GRAY2BGR)
    elif image_np.shape[2] == 4:
        # ignore alpha for CLAHE
        image_np = cv2.cvtColor(image_np, cv2.COLOR_RGBA2RGB)

    # Apply CLAHE to each channel
    clahe = cv2.createCLAHE(clipLimit=5)
    channels = cv2.split(image_np)
    clahe_channels = [np.clip(clahe.apply(c) + 30, 0, 255).astype(np.uint8) for c in channels]
    image_clahe = cv2.merge(clahe_channels)
    
    # Convert back to PIL (ensure "RGB" mode)
    return Image.fromarray(cv2.cvtColor(image_clahe, cv2.COLOR_BGR2RGB))

def apply_vendor_inclusion_zones(image_PIL, input_directory_str, vendor_inclusion_zones_dict, ocr_settings_dict):
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

def preprocess_image(image, input_directory_str, vendor_inclusion_zones_dict, ocr_settings_dict):
    # Preprocess the image by optionally converting to black and white, increasing contrast via the CLAHE algorithm, and adding vendor inclusion zones.
    result = make_black_and_white(image, ocr_settings_dict)
    result = increase_contrast(result, ocr_settings_dict)
    result = apply_vendor_inclusion_zones(result, input_directory_str, vendor_inclusion_zones_dict, ocr_settings_dict)
    return result
