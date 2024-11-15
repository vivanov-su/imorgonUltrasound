from rapidocr_onnxruntime import RapidOCR
from PIL import Image
from src.box_merger import merge_text_boxes
from src.image_redactor import apply_vendor_exclusion_zones

class OCREngine:
    def __init__(self):
        self.engine = RapidOCR()

    def process_image(self, image_path, vendor_exclusion_zones, settings):
        # Open the image
        with Image.open(image_path) as image:
            # Apply vendor exclusion zones
            modified_image = apply_vendor_exclusion_zones(image, vendor_exclusion_zones)

            # Run OCR on the modified image
            result, _ = self.engine(modified_image)

        # Additionally merge text boxes based on settings
        merged_boxes = merge_text_boxes(result, settings)

        # Collapse boxes into readable output
        text_list = [line[1] for line in merged_boxes]
        return text_list
