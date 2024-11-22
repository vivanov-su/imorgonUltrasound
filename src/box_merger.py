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

def is_within_tolerances(center_a, center_b, width_a, height_a, settings):
    # Check if two boxes centers are within specified tolerances
    max_vertical_offset = settings.get("max_vertical_offset", 0.25)
    max_horizontal_separation = settings.get("max_horizontal_separation", 2.0)
    
    vertical_distance = abs(center_a[1] - center_b[1])
    horizontal_distance = abs(center_a[0] - center_b[0])
    
    return (vertical_distance <= height_a * max_vertical_offset and 
            horizontal_distance <= width_a * max_horizontal_separation)

def post_process(ocr_result, settings):
    merged_results = []
    used_indices = set()
    
    for i, item in enumerate(ocr_result):
        if i in used_indices:
            continue

        # Optionally discard if detected text is not a proper sonography term
        
        box_i, (text_i, confidence_i) = item
        center_i = compute_center_of_mass(box_i)
        width_i, height_i = compute_bounding_box_dimensions(box_i)
        
        merged_text = text_i
        min_confidence = confidence_i
        merge_needed = False
        
        for j in range(i + 1, len(ocr_result)):
            if j in used_indices:
                continue
            
            box_j, (text_j, confidence_j) = ocr_result[j]
            center_j = compute_center_of_mass(box_j)
            
            # Still using the width_i and height_i based on its bounding box
            if is_within_tolerances(center_i, center_j, width_i, height_i, settings):
                # Merge the texts and update the confidence
                merged_text += ' ' + text_j
                min_confidence = min(min_confidence, confidence_j)
                used_indices.add(j)
                merge_needed = True
        
        if merge_needed:
            # Calculate new bounding box encompassing both boxes
            merged_results.append((box_i, (merged_text, min_confidence)))
        else:
            merged_results.append((box_i, (text_i, confidence_i)))

    return merged_results
