# Specific engine may be freely switched out
from rapidocr_onnxruntime import RapidOCR
from paddleocr import PaddleOCR
import numpy as np

class OCREngine:
    ocr_engine_choice = None

    def __init__(self, ocr_settings):
        # Extract the OCR engine choice from the settings
        self.ocr_engine_choice = ocr_settings.get("ocr_engine", None)
        print(f"### Using OCR engine: {self.ocr_engine_choice}")

        if self.ocr_engine_choice == "RapidOCR": self.engine = RapidOCR()
        elif self.ocr_engine_choice == "PaddleOCR": self.engine = PaddleOCR(use_angle_cls=True, lang="en")
        else: raise ValueError(f"Unsupported OCR engine!")

    def formatOutput(self, raw_output):
        if self.ocr_engine_choice == "RapidOCR": return self.formatRapidOCR(raw_output)
        elif self.ocr_engine_choice == "PaddleOCR": return self.formatPaddleOCR(raw_output)

    def formatRapidOCR(self, raw_output):
        result, _ = raw_output
        return result

    def formatPaddleOCR(self, raw_output):
        result = []
        for ocr_result in raw_output[0]:
            # Unpack the current element
            list_part, tuple_part = ocr_result

            # Create a new element with extracted tuple items
            new_element = [list_part] + list(tuple_part)

            # Append the transformed element to the result list
            result.append(new_element)
        return result

    def run_ocr(self, image):
        if self.ocr_engine_choice == "RapidOCR": output = self.engine(image)
        elif self.ocr_engine_choice == "PaddleOCR": output = self.engine.ocr(np.array(image))

        # OCR results must come in the form of:
        # [[[x1, y1], [x2, y2], [x3, y3], [x4, y4]], "TEXT", confidence]
        formatted = self.formatOutput(output)
        return formatted
