import cv2
import numpy as np
from tqdm import tqdm

from ocr.utils.text_utils import ocr, get_text_bounding_box
from ocr.utils.text_region_detection import *
from ocr.utils.text_line_detection import text_line_detection

# Remove background and get text bounding boxes
def remove_background(img_array, net, dilate=True):
    print('REMOVING BACKGROUND')
    # Text box detection
    bboxes = get_text_bounding_box(img_array, net)
   
    # Create mask
    mask = np.zeros((img_array.shape[0], img_array.shape[1]))
    color = 255
    for box in bboxes:
        mask = cv2.rectangle(mask, box[0].astype('int32'), box[2].astype('int32'), color, -1)
    
    if dilate:
        # Create rectangular structuring element and dilate
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (13,13))
        mask = cv2.dilate(mask, kernel, iterations=1)
    mask = cv2.bitwise_not(mask.astype('uint8')) # Inverse mask

    img_array = (img_array*(np.expand_dims(cv2.bitwise_not(mask)/255, axis=2))+np.expand_dims(mask, axis=2)).astype('uint8')
    return img_array, bboxes

def intersection(a,b):
    x = max(a[0], b[0])
    y = max(a[1], b[1])
    w = min(a[0]+a[2], b[0]+b[2]) - x
    h = min(a[1]+a[3], b[1]+b[3]) - y
    if w<0 or h<0: return () # or (0,0,0,0) ?
    return (x, y, w, h)

# Find min line height for each text region
def find_min_height(metadata, bboxes):
    print('FIND MIN LINE HEIGHT FOR EACH REGION')
    
    # Getting all intersection area between text blocks and text regions
    inter_area_text_box_region = []
    for box in bboxes:
        x = int(box[0][0])
        y = int(box[0][1])
        w = int(box[2][0]) - int(box[0][0])
        h = int(box[2][1]) - int(box[0][1])
        temp = {}
        for idx, region in enumerate(metadata):
            inter_area = intersection((x, y, w, h), region['text-region'])
            # If intersect and percentage of intersect is greater than 0.8 => take that box
            if len(inter_area) != 0 and inter_area[2]*inter_area[3]/w*h > 0.8:
                temp[idx] = inter_area[2]*inter_area[3]
        inter_area_text_box_region.append(temp)
    
    # Map text box to text region
    box_region_mapping = {}
    for box_idx, area in enumerate(inter_area_text_box_region):
        if len(area) != 0:
            # If text block doesn't in any text region => continue
            # Else map text box to largest intersection area
            region_idx = max(area, key=area.get)
            if region_idx not in box_region_mapping:
                box_region_mapping[region_idx] = []
            box_region_mapping[region_idx].append(box_idx)
    
    # Get minium line height for each region
    for region_idx, box_idx_list in box_region_mapping.items():
        h_list = [int(bboxes[i][2][1]) - int(bboxes[i][0][1]) for i in box_idx_list]
        min_line_height = min(h_list)/4
        metadata[region_idx]['min_line_height'] = min_line_height
    
    new_metadata = []
    for meta in metadata:
        # Some region doesn't contain any text => remove it
        if 'min_line_height' in meta:
            new_metadata.append(meta)

    return new_metadata

def ocr_text(img, detector, net):
    # OCR theo ảnh gốc
    org_img = img.copy()
    # Loại bỏ background để lấy thông tin bounding box đoạn văn chính xác
    preprocess_img, bboxes = remove_background(img, net)
    text_metadata = text_region_detection(preprocess_img, dilate_kernel=(5,4))

    text_metadata = find_min_height(text_metadata, bboxes)
    
    new_text_metadata = []
    print('GET LINE REGION AND OCR')
    for metadata in tqdm(text_metadata):
        x_text = metadata['text-region'][0]
        y_text = metadata['text-region'][1]
        w_text = metadata['text-region'][2]
        h_text = metadata['text-region'][3]
        # Lấy ảnh đoạn văn (với ảnh gốc và ảnh tiền xử lý)
        org_text_region = org_img[y_text:y_text+h_text, x_text:x_text+w_text]
        preprocess_text_region = preprocess_img[y_text:y_text+h_text, x_text:x_text+w_text]
        lines = text_line_detection(preprocess_text_region, metadata['min_line_height'])
        lines_metadata = []
        for line in lines:
            x_line = line[0]
            y_line = line[1]
            w_line = line[2]
            h_line = line[3]
            # Lấy dòng chưa cắt vùng thừa trái phải (với ảnh đã preprocess loại bỏ background)
            line_region = preprocess_text_region[y_line:y_line+h_line, x_line:x_line+w_line]
            # Lấy vị trí trái phải mới
            new_x_line, new_w_line = preprocess_line_region(line_region)
            # Lấy dòng đã cắt vùng thừa trái phải (với ảnh gốc)
            new_line_region = org_text_region[y_line:y_line+h_line, new_x_line:new_x_line+new_w_line]
            text = ocr(new_line_region, detector)
            lines_metadata.append({'line_coordinates': [int(new_x_line)+x_text, int(y_line)+y_text, int(new_w_line), int(h_line)], 'text': text})
        new_text_metadata.append(lines_metadata)
    return new_text_metadata

def metadata_to_text(metadata):
    text=''
    for paragraph in metadata:
        paragraph_text = ''
        for line in paragraph:
            paragraph_text+=line['text']+'\n'
        text += paragraph_text.strip() + '\n\n'
    return text.strip()
    