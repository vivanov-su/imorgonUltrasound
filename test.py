import os
import time
import subprocess
import yaml

def calculate_differences(output_keywords, expected_keywords):
    """
    Calculate missing and additional keywords for a single file.
    """
    missing_keywords = [kw for kw in expected_keywords if kw not in output_keywords]
    additional_keywords = [kw for kw in output_keywords if kw not in expected_keywords]
    return missing_keywords, additional_keywords

def compare_outputs(output_dir, results_dir, vendor_dir):
    """
    Compare the OCR results for a vendor and report differences.
    """
    output_file_path = os.path.join(output_dir, vendor_dir, "ocr_results.yaml")
    expected_file_path = os.path.join(results_dir, vendor_dir, "ocr_results.yaml")

    # Check if required files exist
    if not os.path.exists(output_file_path):
        print(f"[ERROR] OCR output file missing for {vendor_dir}. Skipping...")
        return []

    if not os.path.exists(expected_file_path):
        print(f"[ERROR] Expected results file missing for {vendor_dir}. Skipping...")
        return []

    # Load data
    with open(output_file_path, 'r') as f:
        output_data = yaml.safe_load(f)
    with open(expected_file_path, 'r') as f:
        expected_data = yaml.safe_load(f)

    # Calculate differences
    total_expected, total_missing = 0, 0
    differences = []

    for file_name, output_keywords in output_data.items():
        expected_keywords = expected_data.get(file_name, [])
        missing, additional = calculate_differences(output_keywords, expected_keywords)

        # Gather stats
        total_expected += len(expected_keywords)
        total_missing += len(missing)

        if missing or additional:
            differences.append({
                "file": file_name,
                "missing": missing,
                "additional": additional
            })

    # Report differences
    for diff in differences:
        print(f"[{vendor_dir}] {diff['file']}:")
        if diff["missing"]:
            percentage_missing = (len(diff["missing"]) / len(expected_data.get(diff["file"], []))) * 100 if expected_data.get(diff["file"]) else 0
            print(f"  - Missing ({percentage_missing:.2f}%): {', '.join(diff['missing'])}")
        if diff["additional"]:
            print(f"  - Additional: {', '.join(diff['additional'])}")

    # Print overall summary for vendor
    if total_expected > 0:
        overall_missing_percentage = (total_missing / total_expected) * 100
        print(f"[{vendor_dir}] Overall miss percentage: {overall_missing_percentage:.2f}%\n")
    else:
        print(f"[{vendor_dir}] No expected keywords to compare.\n")

    return differences

def run_tests():
    """
    Main function to run all tests across vendors.
    """
    # Define paths
    test_cases_dir = "./testing/test_images"
    output_dir = "./testing/ocr_output"
    results_dir = "./testing/true_results"
    valid_keywords_path = "./valid_annotation_keywords.yaml"
    inclusion_zones_path = "./vendor_inclusion_zones.yaml"

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Get vendor directories
    vendor_dirs = sorted(
        d for d in os.listdir(test_cases_dir) if os.path.isdir(os.path.join(test_cases_dir, d))
    )
    if not vendor_dirs:
        print("[INFO] No vendor directories found. Exiting.")
        return

    total_time, total_images, all_differences = 0, 0, []

    for vendor_dir in vendor_dirs:
        print(f"[INFO] Running test case for {vendor_dir}...")

        # Paths for vendor-specific input and output
        input_dir = os.path.join(test_cases_dir, vendor_dir)
        vendor_output_dir = os.path.join(output_dir, vendor_dir)
        os.makedirs(vendor_output_dir, exist_ok=True)

        # Count images
        image_files = [f for f in os.listdir(input_dir) if f.lower().endswith((".png", ".jpg", ".jpeg", ".tiff", ".gif"))]
        num_images = len(image_files)

        if num_images == 0:
            print(f"[WARNING] No images found for {vendor_dir}. Skipping...\n")
            continue

        # Run OCR processing
        start_time = time.time()
        subprocess.run(
            ["python", "executable.py", input_dir, vendor_output_dir],
            stdout = subprocess.DEVNULL
        )
        elapsed_time = time.time() - start_time

        # print(f"[INFO] Processed  in {elapsed_time:.2f} seconds.")
        print(f"{num_images} images, average time: {elapsed_time / num_images:.2f} seconds/image\n")

        # Update aggregate metrics
        total_time += elapsed_time
        total_images += num_images

        # Compare results and track differences
        differences = compare_outputs(output_dir, results_dir, vendor_dir)
        all_differences.extend(differences)

    # Print test summary
    print("\n[INFO] All test cases completed.")
    if total_images > 0:
        print(f"Total images processed: {total_images}")
        print(f"Total time taken: {total_time:.2f} seconds")
        print(f"Average processing time per image: {total_time / total_images:.2f} seconds/image")
    else:
        print("[INFO] No images were processed.")

    if all_differences:
        print("\n[INFO] Summary of differences:")
        for diff in all_differences:
            print(f"{diff['file']}:")
            if diff["missing"]:
                print(f"  - Missing: {', '.join(diff['missing'])}")
            if diff["additional"]:
                print(f"  - Additional: {', '.join(diff['additional'])}")
    else:
        print("[INFO] No differences found between outputs and expected results.")

if __name__ == "__main__":
    run_tests()
