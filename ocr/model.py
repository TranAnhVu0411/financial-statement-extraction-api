from ocr.path import SIGNATURE_LOGO_DETECTION_PATH, TABLE_DETECTION_PATH, TABLE_STRUCTURE_RECOGNITION_PATH
# from ocr.utils.load_models import Signver_clean_model
from ocr.utils.load_models import YOLOv5_model, VietOCR_model, CRAFT_model

signature_logo_detection = YOLOv5_model(SIGNATURE_LOGO_DETECTION_PATH)
# cleaner = Signver_clean_model()
table_detection = YOLOv5_model(TABLE_DETECTION_PATH, threshold=True)
detector = VietOCR_model()
net = CRAFT_model()
tsr_model = YOLOv5_model(TABLE_STRUCTURE_RECOGNITION_PATH)