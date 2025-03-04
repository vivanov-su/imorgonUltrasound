import os
import sys
import yaml
import time
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
            "keywords": list(ocr_keywords),
            "true_positives_percent": round(true_positive_percent, 2),
            "false_positives_count": false_positives_count
        }

        total_true_positive_percent += true_positive_percent
        total_false_positives += false_positives_count

    # Calculate overall averages
    engine_performance["avg_true_positives_percent"] = round(total_true_positive_percent / num_images, 2)
    engine_performance["avg_false_positives_count"] = total_false_positives / num_images
    engine_performance["average_time_per_image"] = round(time_taken / num_images, 2)

    return engine_performance


if __name__ == "__main__":
    # Step 1: Get input and output paths
    if len(sys.argv) != 3:
        # Incorrect number of arguments
        print("Usage: python main.py <input_directory> <output_directory>")
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

    # Step 4: Save metrics for all engines to the output directory
    output_file_path = os.path.join(output_directory, "performance_metrics.yaml")
    with open(output_file_path, "w") as output_file:
        yaml.dump(performance_metrics, output_file, default_flow_style=False)
        print(f"### Performance metrics (grouped by engine) saved to {output_file_path}")
