def compute_center_of_mass(box):
    # Calculate the center of mass for a box
    x_coords = [point[0] for point in box]
    y_coords = [point[1] for point in box]
    center_x = sum(x_coords) / len(x_coords)
    center_y = sum(y_coords) / len(y_coords)
    return (center_x, center_y)

def compute_bounding_box_dimensions(box):
    # Calculate the width and height for the axis-aligned bounding box around the quadrilateral
    x_coords = [point[0] for point in box]
    y_coords = [point[1] for point in box]
    width = max(x_coords) - min(x_coords)
    height = max(y_coords) - min(y_coords)
    return width, height

def post_process(ocr_results, valid_annotation_keywords_dict, ocr_settings_dict):
    if ocr_results is None:
        return []

    valid_keywords = valid_annotation_keywords_dict.get("valid_annotation_keywords", None)
    require_valid_keyword = ocr_settings_dict.get("require_valid_keyword", False)

    processed_results = []
    
    for item in ocr_results:
        # Unpack the OCR result box and text with confidence
        box, text, confidence = item

        # If valid keywords are required, filter results based on the presence of valid keywords
        if require_valid_keyword:
            if not any(keyword in text.upper() for keyword in valid_keywords):
                continue  # Skip this box if it doesn't match any valid keywords

        # Split the detected text into individual words
        words = text.split()
        
        # Create a result entry for each word
        for word in words:
            if require_valid_keyword:
                # Check if the word matches any valid keywords
                if not any(keyword in word.upper() for keyword in valid_keywords):
                    continue  # Skip this word if it doesn't match any valid keywords
            
            # Add the word and its associated box to the results
            # NOTE: The box is still associated with the entire original sentence
            processed_results.append((box, (word, confidence)))

    # Extract only the readable text portion from all processed results
    readable_results = [item[1][0] for item in processed_results]

    return readable_results
