from vietocr.tool.predictor import Predictor
from vietocr.tool.config import Cfg
import torch
from CRAFT_pytorch.craft import CRAFT
from CRAFT_pytorch.test import copyStateDict
# from signver.signver.cleaner.cleaner import Cleaner
import os
from dotenv import load_dotenv

load_dotenv()

def VietOCR_model():
    # Load vietOCR model
    config = Cfg.load_config_from_name('vgg_transformer')
    config['cnn']['pretrained']=False
    config['device'] = 'cpu'
    detector = Predictor(config)
    return detector

def YOLOv5_model(model_path, yolo_path = os.path.join(os.getenv('WORKING_DIR'), os.getenv('YOLOV5_PATH')), threshold = False):
    # Load YOLOV5 model
    model = torch.hub.load(
        yolo_path,
        'custom',
        source='local',
        path = model_path,
        force_reload = True)
    if threshold:
        model.conf = 0.7
    return model

def CRAFT_model(model_path = os.path.join(os.getenv('WORKING_DIR'), os.getenv('CRAFT_PATH'))):
    net = CRAFT()
    net.load_state_dict(copyStateDict(torch.load(model_path, map_location='cpu')))
    net.eval()
    return net

# def Signver_clean_model(model_path = SIGNATURE_CLEANER_PATH):
#     # Load signature cleaner model
#     cleaner_model_path = model_path
#     cleaner = Cleaner()
#     cleaner.load(cleaner_model_path)
#     return cleaner