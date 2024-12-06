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

def is_within_tolerances(center_a, center_b, width_a, height_a):
    # Check if two boxes centers are within specified tolerances
    MAX_VERTICAL_OFFSET = 0.25
    MAX_HORIZONTAL_SEPARATION = 2.0
    
    vertical_distance = abs(center_a[1] - center_b[1])
    horizontal_distance = abs(center_a[0] - center_b[0])
    
    return (vertical_distance <= height_a * MAX_VERTICAL_OFFSET and 
            horizontal_distance <= width_a * MAX_HORIZONTAL_SEPARATION)

def post_process(ocr_result, valid_annotation_keywords_dict):
    valid_keywords = valid_annotation_keywords_dict.get("valid_annotation_keywords", None)
    merged_results = []
    used_indices = set()
    
    for i, item in enumerate(ocr_result):
        if i in used_indices:
            continue

        # Unpack the OCR result box and text with confidence
        box_i, text_i, confidence_i = item

        # Check if detected text contains any valid keywords
        if not any(keyword in text_i.upper() for keyword in valid_keywords):
            continue  # Skip this box if it doesn't match any valid keywords

        center_i = compute_center_of_mass(box_i)
        width_i, height_i = compute_bounding_box_dimensions(box_i)
        
        merged_text = text_i
        min_confidence = confidence_i
        merge_needed = False
        
        for j in range(i + 1, len(ocr_result)):
            if j in used_indices:
                continue
            
            box_j, text_j, confidence_j = ocr_result[j]

            # Check if the text of the other box contains any valid keywords
            if not any(keyword in text_j.upper() for keyword in valid_keywords):
                continue  # Skip this box if it doesn't match any valid keywords

            center_j = compute_center_of_mass(box_j)
            
            # Check if two boxes are close enough to merge based on tolerances
            if is_within_tolerances(center_i, center_j, width_i, height_i):
                # Merge the texts and update the confidence
                merged_text += ' ' + text_j
                min_confidence = min(min_confidence, confidence_j)
                used_indices.add(j)
                merge_needed = True
        
        if merge_needed:
            # Append merged result
            merged_results.append((box_i, (merged_text, min_confidence)))
        else:
            # Append as is
            merged_results.append((box_i, (text_i, confidence_i)))

    return merged_results
