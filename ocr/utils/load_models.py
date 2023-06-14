from vietocr.tool.predictor import Predictor
from vietocr.tool.config import Cfg
import torch
from CRAFT_pytorch.craft import CRAFT
from CRAFT_pytorch.test import copyStateDict
from signver.signver.cleaner.cleaner import Cleaner
from ocr.path import YOLOV5_PATH, CRAFT_PATH, SIGNATURE_CLEANER_PATH

def VietOCR_model():
    # Load vietOCR model
    config = Cfg.load_config_from_name('vgg_transformer')
    config['cnn']['pretrained']=False
    config['device'] = 'cpu'
    detector = Predictor(config)
    return detector

def YOLOv5_model(model_path, yolo_path = YOLOV5_PATH):
    # Load YOLOV5 model
    model = torch.hub.load(
        yolo_path,
        'custom',
        source='local',
        path = model_path,
        force_reload = True)
    return model

def CRAFT_model(model_path = CRAFT_PATH):
    net = CRAFT()
    net.load_state_dict(copyStateDict(torch.load(model_path, map_location='cpu')))
    net.eval()
    return net

def Signver_clean_model(model_path = SIGNATURE_CLEANER_PATH):
    # Load signature cleaner model
    cleaner_model_path = model_path
    cleaner = Cleaner()
    cleaner.load(cleaner_model_path)
    return cleaner