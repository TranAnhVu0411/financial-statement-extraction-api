# from ocr.utils.load_models import Signver_clean_model
from ocr.utils.load_models import YOLOv5_model, VietOCR_model, CRAFT_model
import os
from dotenv import load_dotenv

load_dotenv()
signature_logo_detection = YOLOv5_model(os.path.join(os.getenv('WORKING_DIR'), os.getenv('SIGNATURE_LOGO_DETECTION_PATH')))
# cleaner = Signver_clean_model()
table_detection = YOLOv5_model(os.path.join(os.getenv('WORKING_DIR'), os.getenv('TABLE_DETECTION_PATH')), threshold=True)
detector = VietOCR_model()
net = CRAFT_model()
tsr_model = YOLOv5_model(os.path.join(os.getenv('WORKING_DIR'), os.getenv('TABLE_STRUCTURE_RECOGNITION_PATH')))