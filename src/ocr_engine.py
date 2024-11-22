# Specific engine may be freely switched out
from rapidocr_onnxruntime import RapidOCR

class OCREngine:
    def __init__(self):
        # Engine initialization. Takes up as much time as processing an image
        self.engine = RapidOCR()

    def run_ocr(self, image):
        # Raw OCR results in the form of:
        # [[[x1, y1], [x2, y2], [x3, y3], [x4, y4]], ['TEXT', confidence]]
        result, _ = self.engine(image)
        return result
