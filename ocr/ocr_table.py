import numpy as np
from tqdm import tqdm

from ocr.utils.text_utils import ocr, get_text_bounding_box
from ocr.utils.text_region_detection import *
from ocr.utils.text_line_detection import text_line_detection
from ocr.utils.load_models import YOLOv5_model, CRAFT_model, VietOCR_model
from ocr.utils.table_structure_postprocess import objects_to_cells
import ocr.utils.table_config as table_config
from ocr.preprocess import deskew, remove_line
from ocr.path import TABLE_STRUCTURE_RECOGNITION_PATH

def get_table_text_object(img, net):
    boxes = get_text_bounding_box(img, net)
    tokens_in_table = [np.array([box[0].astype('int32'), box[2].astype('int32')]).flatten().tolist() for box in boxes]
    return tokens_in_table

def table_structure_recognition(image, model):
    print('TABLE STRUCTURE DETECTION')
    pred = model(image, size=640)
    pred = pred.xywhn[0]    
    result = pred.numpy()
    return result

def convert_structure(img, tsr_result, tokens_in_table):
    print('CLEAN TABLE STRUCTURE')
    width = img.shape[1]
    height = img.shape[0]
    bboxes = []
    scores = []
    labels = []
    for item in tsr_result:
        class_id = int(item[5])
        score = float(item[4])
        min_x = item[0]
        min_y = item[1]
        w = item[2]
        h = item[3]
        
        x1 = int((min_x-w/2)*width)
        y1 = int((min_y-h/2)*height)
        x2 = int((min_x+w/2)*width)
        y2 = int((min_y+h/2)*height)

        bboxes.append([x1, y1, x2, y2])
        scores.append(score)
        labels.append(class_id)

    table_objects = []
    for bbox, score, label in zip(bboxes, scores, labels):
        table_objects.append({'bbox': bbox, 'score': score, 'label': label})
        
    table = {'objects': table_objects, 'page_num': 0}
    table_structures, cells, confidence_score = objects_to_cells(table, table_objects, tokens_in_table, table_config.structure_class_names, table_config.structure_class_thresholds)
    return table_structures, cells, confidence_score

def ocr_cell(img, min_line_height, detector):
    result = ''
    text_cell_metadata = []
    text_metadata = text_region_detection(img, dilate_kernel=(7,7))
    for metadata in text_metadata:
        x_text = metadata['text-region'][0]
        y_text = metadata['text-region'][1]
        w_text = metadata['text-region'][2]
        h_text = metadata['text-region'][3]
        text_region = img[y_text:y_text+h_text, x_text:x_text+w_text]
        lines = text_line_detection(text_region, min_line_height)
        lines_metadata = []
        for line in lines:
            x_line = line[0]
            y_line = line[1]
            w_line = line[2]
            h_line = line[3]
            line_region = text_region[y_line:y_line+h_line, x_line:x_line+w_line]
            new_x_line, new_w_line = preprocess_line_region(line_region)
            new_line_region = text_region[y_line:y_line+h_line, new_x_line:new_x_line+new_w_line]
            text = ocr(new_line_region, detector)
            lines_metadata.append({'line_coordinates': [int(new_x_line), int(y_line), int(new_w_line), int(h_line)], 'text': text})
            result+=text+' '
        text_cell_metadata.append({'region_coordinates': [int(x_text), int(y_text), int(w_text), int(h_text)], 'lines': lines_metadata, 'text': result})

    return text_cell_metadata

def ocr_table_cell(img, cells, ocr_model):
    print('TABLE OCR')
    for cell in tqdm(cells):
        text_metadata = []
        if len(cell['spans'])!=0:
            # Calculate min line height by using text height
            min_line_height = min([bb[3]-bb[1] for bb in cell['spans']])/4
            bbox = cell['bbox']
            x1 = int(bbox[0])
            y1 = int(bbox[1])
            x2 = int(bbox[2])
            y2 = int(bbox[3])
            crop = img[y1:y2, x1:x2]
            text_metadata = ocr_cell(crop, min_line_height, ocr_model)
        cell['text'] = text_metadata
    return cells
    

def ocr_table(img, tsr_model, net, detector):
    print('LOAD MODELS')

    img = deskew(img)
    tokens_in_table = get_table_text_object(img, net)
    tsr_result = table_structure_recognition(img, tsr_model)
    _, cells, _ = convert_structure(img, tsr_result, tokens_in_table)
    img = remove_line(img)
    new_cells = ocr_table_cell(img, cells, detector)
    return new_cells


