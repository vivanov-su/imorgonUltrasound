import os
import sys
import yaml
import time
import itertools
import xlsxwriter
from PIL import Image, ImageDraw
import tempfile
from executable import process_ultrasound_scans
from src.config_loader import load_yaml_config


def compute_metrics(ocr_results_dict, true_results_dict, time_taken, num_images):
    engine_performance = {
        "images": {},
        "avg_true_positives_percent": 0.0,
        "avg_false_positives_count": 0.0,
        "average_time_per_image": 0.0
    }

    total_true_positive_percent = 0.0
    total_false_positives = 0

    for filename, true_keywords in true_results_dict.items():
        ocr_keywords = set(ocr_results_dict.get(filename, []))

        # Calculate true positives
        true_keywords_set = set(true_keywords)
        true_positives = ocr_keywords & true_keywords_set
        false_positives = ocr_keywords - true_keywords_set

        true_positive_percent = len(true_positives) / len(true_keywords_set) if true_keywords_set else 1.0
        false_positives_count = len(false_positives)

        engine_performance["images"][filename] = {
            "expected_keywords": list(true_keywords),
            "detected_keywords": list(ocr_keywords),
            "true_positives_percent": round(true_positive_percent, 2),
            "false_positives_count": false_positives_count,
        }

        total_true_positive_percent += true_positive_percent
        total_false_positives += false_positives_count

    # Calculate overall averages
    engine_performance["avg_true_positives_percent"] = round(total_true_positive_percent / num_images, 2)
    engine_performance["avg_false_positives_count"] = total_false_positives / num_images
    engine_performance["average_time_per_image"] = round(time_taken / num_images, 2)

    return engine_performance

def save_metrics_to_excel(performance_metrics, excel_file_path, input_directory):
    # Create a new Excel workbook and worksheet
    workbook = xlsxwriter.Workbook(excel_file_path)
    worksheet = workbook.add_worksheet("Comparison")

    # Define formats for columns
    percentage_format = workbook.add_format({"num_format": '0%'})  # Format for percentage values

    temporary_files = []  # To track temporary files created during the process

    # Write the headers
    headers = [
        "Image Filename",
        "Expected Keywords",
        "OCR Engine",
        "Detected Keywords",
        "Correctly Detected (%)",
        "Noise Detected (#)",
    ]
    for col, header in enumerate(headers):
        worksheet.write(0, col, header)

    row = 1  # Start writing data from the second row

    # Load the inclusion zones from the YAML file
    with open("vendor_inclusion_zones.yaml", 'r') as f:
        inclusion_zones = yaml.safe_load(f)

    # Write data for each image
    for filename in performance_metrics[next(iter(performance_metrics))]["images"].keys():  # Get filenames from the first engine
        image_path = os.path.join(input_directory, filename)  # Construct full image path

        # Handle image rendering with inclusion zones
        temp_image_path = None
        if os.path.exists(image_path):  # Check if the image exists
            with Image.open(image_path) as img:
                # Gather metadata for zone matching
                img_width, img_height = img.size
                vendor = os.path.basename(os.path.normpath(input_directory))

                # Find the inclusion zones for this vendor and image size
                matched_zones = next(
                    (zone for zone in inclusion_zones.get(vendor, [])
                     if zone["image_size"] == [img_width, img_height]),
                    None
                )

                # Draw the inclusion zones if they exist
                if matched_zones:
                    draw = ImageDraw.Draw(img)
                    for box in matched_zones["boxes"]:
                        top_left = (box[0], box[1])
                        bottom_right = (box[2], box[3])
                        draw.rectangle([top_left, bottom_right], outline="red", width=3)

                # Save the modified image to a temporary file for Excel insertion
                temp_image_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
                temp_image_path = temp_image_file.name
                img.save(temp_image_path, format="PNG")
                temp_image_file.close()
                temporary_files.append(temp_image_path)  # Track the temp file for later cleanup

        # Write the filename and add the image
        worksheet.write(row, 0, filename)  # Image Filename
        if temp_image_path:
            worksheet.insert_image(row + 1, 0, temp_image_path, {"x_scale": 0.5, "y_scale": 0.5})

        # Write the expected keywords
        expected_keywords = ", ".join(sorted(performance_metrics[next(iter(performance_metrics))]["images"][filename]["expected_keywords"]))
        worksheet.write(row, 1, expected_keywords)  # Expected Keywords

        # Write data for each engine
        for engine, metrics in performance_metrics.items():
            image_metrics = metrics["images"].get(filename, {})
            
            worksheet.write(row, 2, engine)  # OCR Engine name
            detected_kw = ", ".join(sorted(image_metrics.get("detected_keywords", [])))  # Detected Keywords
            if detected_kw.startswith('='):
                detected_kw = ' ' + detected_kw  # Edge case where Excel interprets it as formula
            worksheet.write(row, 3, detected_kw)
            worksheet.write(row, 4, image_metrics.get("true_positives_percent", 0.0), percentage_format)  # True Positives Percentage
            worksheet.write(row, 5, image_metrics.get("false_positives_count", 0))  # False Positives Count
            row += 1

        # Leave an empty row after each image's engines
        worksheet.set_row(row, 300)  # Extra space for images themselves
        row += 1

    # Write summary statistics for each engine
    row += 1  # Leave a blank row before summary
    worksheet.write(row, 0, f"Summary: {input_directory}")  # Header for summary statistics
    row += 1

    summary_headers = [
        "OCR Engine",
        "Average True Positives (%)",
        "Average False Positives Count",
        "Average Time Per Image (secs)"
    ]

    for col, header in enumerate(summary_headers):
        worksheet.write(row, col, header)

    row += 1
    for engine, metrics in performance_metrics.items():
        worksheet.write(row, 0, engine)  # OCR Engine
        worksheet.write(row, 1, metrics["avg_true_positives_percent"], percentage_format)  # Avg True Positives (%)
        worksheet.write(row, 2, metrics["avg_false_positives_count"])  # Avg False Positives Count
        worksheet.write(row, 3, metrics["average_time_per_image"])  # Avg Time Per Image (secs)
        row += 1

    # Close the workbook
    workbook.close()

    # Cleanup temporary files after workbook.close()
    for temp_file in temporary_files:
        try:
            if os.path.exists(temp_file):
                os.remove(temp_file)
        except Exception as e:
            print(f"Error deleting temporary file {temp_file}: {e}")

if __name__ == "__main__":
    # Step 1: Get input and output paths
    if len(sys.argv) != 3:
        # Incorrect number of arguments
        print("Usage: python test.py <input_directory> <output_directory>")
        sys.exit(1)

    input_directory = sys.argv[1]
    output_directory = sys.argv[2]
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Step 2: Load configuration
    valid_annotation_keywords = load_yaml_config("valid_annotation_keywords.yaml")
    vendor_inclusion_zones = load_yaml_config("vendor_inclusion_zones.yaml")
    ocr_settings = load_yaml_config("ocr_settings.yaml")

    true_results_yaml_path = os.path.join(input_directory, "true_results.yaml")
    true_results = load_yaml_config(true_results_yaml_path)

    # Step 3: Run each engine on the directory
    performance_metrics = {}
    ocr_engines = ["RapidOCR", "PaddleOCR", "EasyOCR", "DocTR", "Tesseract"]
    for engine in ocr_engines:
        # Step 3a: Configure OCR settings for the current engine
        ocr_settings["ocr_engine"] = engine  # Update the engine dynamically

        # Step 3b: Measure time and run the current engine
        start_time = time.time()  # Start timing
        ocr_results = process_ultrasound_scans(
            input_directory, valid_annotation_keywords, vendor_inclusion_zones, ocr_settings
        )
        end_time = time.time()  # End timing

        time_taken = end_time - start_time  # Compute total time taken
        num_images = len(true_results)

        # Step 3c: Calculate the metrics for engine's results
        performance_metrics[engine] = compute_metrics(ocr_results, true_results, time_taken, num_images)

    # Step 4: Save metrics for all engines to the output directory (YAML format)
    output_yaml_path = os.path.join(output_directory, "performance_metrics.yaml")
    with open(output_yaml_path, "w") as yaml_file:
        yaml.dump(performance_metrics, yaml_file, default_flow_style=False)
        print(f"### Performance metrics (grouped by engine) saved to {output_yaml_path}")

    # Step 5: Save metrics for all engines to the output directory (Excel format)
    output_excel_path = os.path.join(output_directory, "performance_metrics.xlsx")
    save_metrics_to_excel(performance_metrics, output_excel_path, input_directory)
    print(f"### Performance metrics saved to Excel file at {output_excel_path}")
