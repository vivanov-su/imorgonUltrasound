import os
import time
import subprocess
import yaml

def compare_outputs(output_dir, results_dir, vendor_dir):
    """
    Compares the `ocr_results.yaml` file in the `output/vendor_dir` and `results/vendor_dir`.
    Prints missing and additional keywords for each file.
    """
    output_vendor_path = os.path.join(output_dir, vendor_dir, "ocr_results.yaml")
    results_vendor_path = os.path.join(results_dir, vendor_dir, "ocr_results.yaml")

    if not os.path.exists(output_vendor_path):
        print(f"Output file missing for {vendor_dir}. Skipping comparison...")
        return []

    if not os.path.exists(results_vendor_path):
        print(f"Results file missing for {vendor_dir}. Skipping comparison...")
        return []

    # Load the OCR output files
    with open(output_vendor_path, 'r') as f:
        output_data = yaml.safe_load(f)
        
    with open(results_vendor_path, 'r') as f:
        results_data = yaml.safe_load(f)

    # Store differences
    differences = []
    
    for file_name, output_keywords in output_data.items():
        results_keywords = results_data.get(file_name, [])

        # Check for missing and additional keywords
        missing_keywords = [kw for kw in results_keywords if kw not in output_keywords]
        additional_keywords = [kw for kw in output_keywords if kw not in results_keywords]

        if missing_keywords or additional_keywords:
            differences.append({
                'file': file_name,
                'missing': missing_keywords,
                'additional': additional_keywords
            })

    # Report any differences
    for diff in differences:
        print(f"{diff['file']}:")
        if diff['missing']:
            print(f"- Missing: {', '.join(diff['missing'])}")
        if diff['additional']:
            print(f"- Additional: {', '.join(diff['additional'])}")
        print()

    return differences


def run_tests():
    test_cases_dir = "./testing/testCases"
    output_dir = "./testing/output"
    results_dir = "./testing/results"
    valid_annotation_keywords_path = "./valid_annotation_keywords.yaml"
    vendor_inclusion_zones_path = "./vendor_inclusion_zones.yaml"

    # Ensure output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Get a list of test case vendor directories
    vendor_dirs = sorted([d for d in os.listdir(test_cases_dir) if os.path.isdir(os.path.join(test_cases_dir, d)) and d.startswith("vendor")])

    if not vendor_dirs:
        print("No vendor directories found in testCases. Exiting.")
        return

    total_time = 0
    total_images_processed = 0
    total_differences = []

    for vendor_dir in vendor_dirs:
        input_directory = os.path.join(test_cases_dir, vendor_dir)
        vendor_output_dir = os.path.join(output_dir, vendor_dir)

        # Ensure vendor-specific output directory exists
        if not os.path.exists(vendor_output_dir):
            os.makedirs(vendor_output_dir)

        print(f"Running test case for {vendor_dir}...")

        # Count the number of image files in the input directory for this vendor
        num_images = len([f for f in os.listdir(input_directory) if f.lower().endswith((".png", ".jpg", ".jpeg", ".tiff", ".gif"))])

        if num_images == 0:
            print(f"No images found for {vendor_dir}, skipping...")
            continue

        # Time the execution
        start_time = time.time()

        # Run the main script programmatically via subprocess
        subprocess.run([
            "python", "executable.py",
            input_directory,
            vendor_output_dir,
            valid_annotation_keywords_path,
            vendor_inclusion_zones_path
        ])

        end_time = time.time()
        elapsed_time = end_time - start_time

        # Output the results
        print(f"Test case {vendor_dir} completed in {elapsed_time:.2f} seconds.")
        print(f"Number of images processed: {num_images}. Average time per image: {elapsed_time / num_images:.2f} seconds/image\n")

        # Update aggregate metrics
        total_time += elapsed_time
        total_images_processed += num_images

        # Compare outputs and collect differences
        differences = compare_outputs(output_dir, results_dir, vendor_dir)
        if differences:
            total_differences.extend(differences)

    # Print overall test results
    print("All test cases completed.")
    if total_images_processed > 0:
        print(f"Total images processed: {total_images_processed}")
        print(f"Total time taken: {total_time:.2f} seconds")
        print(f"Average processing time per image: {total_time / total_images_processed:.2f} seconds/image")
    else:
        print("No images were processed.")

    # Report differences
    if total_differences:
        print("\nSummary of differences:")
        for diff in total_differences:
            print(f"{diff['file']}:")
            if diff['missing']:
                print(f"- Missing: {', '.join(diff['missing'])}")
            if diff['additional']:
                print(f"- Additional: {', '.join(diff['additional'])}")
            print()
    else:
        print("No differences found between outputs and expected results.")

if __name__ == "__main__":
    run_tests()
