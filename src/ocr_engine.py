from easyocr import Reader
from rapidocr_onnxruntime import RapidOCR
from paddleocr import PaddleOCR
from doctr.models import ocr_predictor
from doctr.io import DocumentFile
import pytesseract
import numpy as np

class OCREngine:
    ocr_engine_choice = None

    def __init__(self, ocr_settings):
        # Extract the OCR engine choice from the settings
        self.ocr_engine_choice = ocr_settings.get("ocr_engine", None)
        print(f"### Using OCR engine: {self.ocr_engine_choice}")

        if self.ocr_engine_choice == "RapidOCR": self.engine = RapidOCR()
        elif self.ocr_engine_choice == "PaddleOCR": self.engine = PaddleOCR(use_angle_cls=True, lang="en")
        elif self.ocr_engine_choice == "EasyOCR": self.engine = Reader(["en"], gpu=False, detector = "dbnet18")
        elif self.ocr_engine_choice == "DocTR": self.engine = ocr_predictor(det_arch="db_resnet50", reco_arch="crnn_vgg16_bn", pretrained=True)
        elif self.ocr_engine_choice == "Tesseract": self.engine = pytesseract
        else: raise ValueError(f"Unsupported OCR engine!")

    def formatOutput(self, raw_output):
        if self.ocr_engine_choice == "RapidOCR": return self.formatRapidOCR(raw_output)
        elif self.ocr_engine_choice == "PaddleOCR": return self.formatPaddleOCR(raw_output)
        elif self.ocr_engine_choice == "EasyOCR": return self.formatEasyOCR(raw_output)
        elif self.ocr_engine_choice == "DocTR": return self.formatDocTR(raw_output)
        elif self.ocr_engine_choice == "Tesseract": return self.formatTesseract(raw_output)

    def formatRapidOCR(self, raw_output):
        result, _ = raw_output
        return result

    def formatPaddleOCR(self, raw_output):
        if raw_output[0] is None:
            return None
        
        result = []
        for ocr_result in raw_output[0]:
            # Unpack the current element
            list_part, tuple_part = ocr_result

            # Create a new element with extracted tuple items
            new_element = [list_part] + list(tuple_part)

            # Append the transformed element to the result list
            result.append(new_element)
        return result

    def formatEasyOCR(self, raw_output):
        result = []
        for ocr_result in raw_output:
            bbox, text, confidence = ocr_result
            bbox_points = [[int(point[0]), int(point[1])] for point in bbox]
            result.append([bbox_points, text, confidence])
        return result

    def formatDocTR(self, raw_output):
        result = []
        
        # "pages" contain all page-level data
        for page in raw_output.export()["pages"]:
            page_width, page_height = page["dimensions"]  # Extract the dimensions of the page
            # Iterate over blocks
            for block in page["blocks"]:
                # Iterate over lines in the block
                for line in block["lines"]:
                    # Iterate over words in the line
                    for word in line["words"]:
                        # Extract text, confidence, and bounding box
                        text = word["value"]
                        confidence = word["confidence"]
                        # Convert normalized bounding box to coordinate points in the image
                        bbox = [
                            [int(coord[0] * page_width), int(coord[1] * page_height)]
                            for coord in [
                                word["geometry"][0],  # Top-left corner
                                (word["geometry"][0][0], word["geometry"][1][1]),  # Bottom-left corner
                                word["geometry"][1],  # Bottom-right corner
                                (word["geometry"][1][0], word["geometry"][0][1])   # Top-right corner
                            ]
                        ]
                        # Append the formatted information
                        result.append([bbox, text, confidence])
        return result

    def formatTesseract(self, raw_output):
        result = []
        for word_data in raw_output:
            # Extract data
            x1, y1, x2, y2, text, confidence = word_data
            bbox = [[x1, y1], [x2, y1], [x2, y2], [x1, y2]]  # Rectangular bounding box
            result.append([bbox, text, float(confidence) / 100])  # Normalize confidence to 0-1
        return result

    def run_tesseract(self, image):
        # Run Tesseract with detailed output
        raw_data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)

        # Extract bounding boxes and other data
        n_boxes = len(raw_data["text"])
        result = []
        for i in range(n_boxes):
            if raw_data["text"][i].strip():  # Skip empty text
                x, y, w, h = raw_data["left"][i], raw_data["top"][i], raw_data["width"][i], raw_data["height"][i]
                text = raw_data["text"][i]
                confidence = raw_data["conf"][i]
                if int(confidence) >= 0:  # Filter invalid confidences
                    result.append([x, y, x + w, y + h, text, confidence])
        return result

    def run_ocr(self, image):
        if self.ocr_engine_choice == "RapidOCR": output = self.engine(image)
        elif self.ocr_engine_choice == "PaddleOCR": output = self.engine.ocr(np.array(image))
        elif self.ocr_engine_choice == "EasyOCR": output = self.engine.readtext(np.array(image), detail=1, paragraph=False)
        elif self.ocr_engine_choice == "DocTR": output = self.engine([np.array(image)])
        elif self.ocr_engine_choice == "Tesseract": output = self.run_tesseract(image)

        # OCR results must come in the form of:
        # [[[x1, y1], [x2, y2], [x3, y3], [x4, y4]], "TEXT", confidence]
        formatted = self.formatOutput(output)
        return formatted
