from pdf2image import convert_from_bytes
import io
from base64 import b64encode

import cv2
import numpy as np
from wand.image import Image as wand_image
from PIL import Image, ImageEnhance

from signver.signver.utils.data_utils import resnet_preprocess
from tqdm import tqdm

# Use cv2 image format
# Deskew image
def deskew(img_array, write_on_terminal=True):
    img_str = cv2.imencode('.jpg', img_array)[1].tobytes()
    if write_on_terminal:
        print('DESKEW')
    with wand_image(blob=img_str) as img:
        img.deskew(0.4*img.quantum_range)
        deskew = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    return deskew

# Increase contrast
def contrast_adjustment(img_array, write_on_terminal=True):
    if write_on_terminal:
        print('INCREASE CONTRAST')
    img = Image.fromarray(img_array)
    enhancer = ImageEnhance.Contrast(img)
    factor = 1.5
    contrast = np.array(enhancer.enhance(factor))
    return contrast

# Remove stamp
def remove_stamp(img_array, write_on_terminal=True):
    if write_on_terminal:
        print('REMOVE STAMP')
    remove_stamp = img_array.copy()
    img_array = cv2.cvtColor(img_array, cv2.COLOR_BGR2HSV)
    
    # lower mask (0-10)
    lower_red = np.array([0,50,50])
    upper_red = np.array([10,255,255])
    mask0 = cv2.inRange(img_array, lower_red, upper_red)

    # upper mask (170-180)
    lower_red = np.array([155,25,0])
    upper_red = np.array([179,255,255])
    mask1 = cv2.inRange(img_array, lower_red, upper_red)

    # join masks
    mask = mask0+mask1

    remove_stamp = (remove_stamp*(np.expand_dims(cv2.bitwise_not(mask)/255, axis=2))+np.expand_dims(mask, axis=2)).astype('uint8')
    return remove_stamp

# Signature remove
def signature_remove(img_array, detection, cleaner, write_on_terminal=True):
    if write_on_terminal:
        print('SIGNATURE DETECTION')
    remove_signature = img_array.copy()
    results = detection([img_array], size=640)  # includes NMS
    signature_metadata = []
    if len(results.xyxy[0])!=0:    
        for sign_coord in results.xyxy[0]:
            x0 = int(sign_coord[0])
            y0 = int(sign_coord[1])
            x1 = int(sign_coord[2])
            y1 = int(sign_coord[3])
            signature_metadata.append({
                'coordinates': (x0, y0, x1, y1),
                'crop_image': remove_signature[y0:y1, x0:x1]
            })
    
    if write_on_terminal:
        print('SIGNATURE CLEANING')
    mask_metadata = []
    if len(signature_metadata)!=0:
        signatures = []
        for metadata in signature_metadata:
            signatures.append(metadata['crop_image'])

        # Feature extraction with resnet model
        sigs= [ resnet_preprocess( x, resnet=False, invert_input=False ) for x in signatures ]

        # Normalization and clean
        norm_sigs = [ x * (1./255) for x in sigs]
        cleaned_sigs = cleaner.clean(np.array(norm_sigs))

        # Reverse normalization
        rev_norm_sigs = [ x / (1./255) for x in cleaned_sigs]

        # Resize and binarization
        for i in range(len(rev_norm_sigs)):
            img_resize = cv2.resize(
                rev_norm_sigs[i].astype('uint8'),
                (signatures[i].shape[1], signatures[i].shape[0]),
                interpolation = cv2.INTER_CUBIC
            )
            img_gray = cv2.cvtColor(img_resize, cv2.COLOR_BGR2GRAY)
            _, mask = cv2.threshold(img_gray, 150, 255, cv2.THRESH_BINARY_INV)
            mask_metadata.append({
                'coordinates': signature_metadata[i]['coordinates'],
                'mask': mask
            })

    if len(mask_metadata)!=0:
        img_mask = np.zeros((remove_signature.shape[0], remove_signature.shape[1])).astype('uint8')
        for metadata in mask_metadata:
            x0 = metadata['coordinates'][0]
            y0 = metadata['coordinates'][1]
            x1 = metadata['coordinates'][2]
            y1 = metadata['coordinates'][3]
            img_mask[y0:y1, x0:x1] = metadata['mask']

        remove_signature = (remove_signature*(np.expand_dims(cv2.bitwise_not(img_mask)/255, axis=2))+np.expand_dims(img_mask, axis=2)).astype('uint8')
    return remove_signature

# For table preprocessing
def remove_line(image, write_on_terminal=True):
    if write_on_terminal:
        print('REMOVE LINE')
    result = image.copy()
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    # Remove horizontal lines
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40,1))
    remove_horizontal = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, horizontal_kernel, iterations=2)
    cnts = cv2.findContours(remove_horizontal, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]
    for c in cnts:
        cv2.drawContours(result, [c], -1, (255,255,255), 5)

    # Remove vertical lines
    vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1,40))
    remove_vertical = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, vertical_kernel, iterations=2)
    cnts = cv2.findContours(remove_vertical, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]
    for c in cnts:
        cv2.drawContours(result, [c], -1, (255,255,255), 5)
    return result

def preprocess_image(img, signature_logo_detection, cleaner):
    img = deskew(img, write_on_terminal=False)
    img = contrast_adjustment(img, write_on_terminal=False)
    img = remove_stamp(img, write_on_terminal=False)
    img = signature_remove(img, signature_logo_detection, cleaner, write_on_terminal=False)
    return img

def convert_image_to_base64(pil_img):
    img_byte_arr = io.BytesIO()
    pil_img.save(img_byte_arr, format='JPEG')
    img_byte_arr = img_byte_arr.getvalue()
    img_b64_string = b64encode(img_byte_arr).decode()
    img_b64_string = img_b64_string.replace('\n', '')
    img_b64_string = 'data:image/jpeg;base64,' + img_b64_string
    return img_b64_string

# Convert pdf to list of images and preprocess
def convert_pdf2images_and_preprocess(pdf, signature_logo_detection, cleaner):
    print('CONVERT_PDF2IMAGES')
    images = convert_from_bytes(pdf)
    base64_images = []
    print('PREPROCESS IMAGES')
    for image in tqdm(images):
        # Make copy and preprocess image
        image_copy = image.copy()
        image_copy = np.array(image_copy)
        image_copy = cv2.cvtColor(image_copy, cv2.COLOR_RGB2BGR) # convert RGB to BGR since preprocess is used OpenCV image format
        image_copy = preprocess_image(image_copy, signature_logo_detection, cleaner)
        image_copy = cv2.cvtColor(image_copy, cv2.COLOR_BGR2RGB) # reconvert BGR to RGB
        image_copy = Image.fromarray(image_copy.astype('uint8')).convert('RGB')
        base64_images.append({'original': convert_image_to_base64(image), 'preprocess': convert_image_to_base64(image_copy)})

    return base64_images

# Seperate image into two part: Text image and Table images
def seperate_image(image, detection, write_on_terminal=True):
    if write_on_terminal:
        print('SEPERATE IMAGE')
    results = detection([image], size=640)  # includes NMS
    image_copy = image.copy()
    table_images = []
    if len(results.xyxy[0])!=0:    
        for table_coord in results.xyxy[0]:
            x0 = int(table_coord[0])
            y0 = int(table_coord[1])
            x1 = int(table_coord[2])
            y1 = int(table_coord[3])
            table_images.append({'table_coordinate': (x0, y0, x1-x0, y1-y0), 'image': image_copy[y0:y1, x0:x1]})
            image = cv2.rectangle(image, (x0, y0), (x1, y1), (255, 255, 255), -1)
    return {'text': image, 'tables': table_images}

def table_text_seperator(img, table_detection):
    # Load table detection models
    seperate_results = seperate_image(img, table_detection)
    return seperate_results