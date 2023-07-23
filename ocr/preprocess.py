import io
from base64 import b64encode
import cv2
import numpy as np
from tqdm import tqdm
import ast
import math

# Signature processing
from signver.signver.utils.data_utils import resnet_preprocess

# deskew library
import pytesseract
# from deskew import determine_skew
from wand.image import Image as wand_image

# Contrast check and enhancement
from skimage.exposure import is_low_contrast
from PIL import Image, ImageEnhance

# PDF 2 images library
import fitz
# from pdf2image import convert_from_bytes, pdfinfo_from_bytes

# Use cv2 image format
# Deskew image
def tryeval(val):
    try:
        val = ast.literal_eval(val)
    except ValueError:
        pass
    return val

def rotate_straight(image, angle, background):
    old_width, old_height = image.shape[:2]
    angle_radian = math.radians(angle)
    width = abs(np.sin(angle_radian) * old_height) + abs(np.cos(angle_radian) * old_width)
    height = abs(np.sin(angle_radian) * old_width) + abs(np.cos(angle_radian) * old_height)

    image_center = tuple(np.array(image.shape[1::-1]) / 2)
    rot_mat = cv2.getRotationMatrix2D(image_center, angle, 1.0)
    rot_mat[1, 2] += (width - old_width) / 2
    rot_mat[0, 2] += (height - old_height) / 2
    return cv2.warpAffine(image, rot_mat, (int(round(height)), int(round(width))), borderValue=background)

def deskew(img_array, write_on_terminal=True):
    if write_on_terminal:
        print('DESKEW')
    try:
        # Rotate 90, 180, 270
        d = pytesseract.image_to_osd(img_array, config='--psm 0')
        ocr_metadata_result = dict((a.strip(), tryeval(b.strip()))  
                                    for a, b in (element.split(': ')  
                                                for element in d.strip().split('\n')))
        rotate_mode = -1
        if ocr_metadata_result['Rotate'] == 90:
            rotate_mode = 0
        elif ocr_metadata_result['Rotate'] == 180:
            rotate_mode = 1
        elif ocr_metadata_result['Rotate'] == 270:
            rotate_mode = 2
        if rotate_mode != -1:
            img_array = cv2.rotate(img_array, rotate_mode)
        img_array_rotate = img_array.copy()
        # Deskew image
        img_str = cv2.imencode('.jpg', img_array)[1].tobytes()

        # With wand imagemagick library
        with wand_image(blob=img_str) as img:
            img.deskew(0.4*img.quantum_range)
            deskew = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

        # # With deskew library
        # grayscale = cv2.cvtColor(img_str, cv2.COLOR_BGR2GRAY)
        # angle = determine_skew(grayscale, min_angle=-5, max_angle=5, min_deviation=0.1)
        # deskew = rotate_straight(img_str, angle, (255, 255, 255))

        return img_array_rotate, deskew
    except:
        img_array_rotate = img_array.copy()
        img_str = cv2.imencode('.jpg', img_array)[1].tobytes()

        # With wand imagemagick library
        with wand_image(blob=img_str) as img:
            img.deskew(0.4*img.quantum_range)
            deskew = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

        # With deskew library
        # grayscale = cv2.cvtColor(img_str, cv2.COLOR_BGR2GRAY)
        # angle = determine_skew(grayscale, min_angle=-5, max_angle=5, min_deviation=0.1)
        # deskew = rotate_straight(img_str, angle, (255, 255, 255))
        
        return img_array_rotate, deskew

# Increase contrast
def contrast_adjustment(img_array, write_on_terminal=True):
    if write_on_terminal:
        print('INCREASE CONTRAST')
    out = is_low_contrast(img_array, fraction_threshold=0.3)
    if out:
        img = Image.fromarray(img_array)
        enhancer = ImageEnhance.Contrast(img)
        factor = 1.5
        contrast = np.array(enhancer.enhance(factor))
        return contrast
    else:
        return img_array

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
    yolo_results = detection([img_array], size=640)  # includes NMS
    # Pretrained nhận diện chữ ký và logo, nhưng ở đây ta chỉ cần loại bỏ chữ ký
    results = [i for i in yolo_results.xyxy[0] if i[5]==1]
    signature_metadata = []
    if len(results)!=0:    
        for sign_coord in results:
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
    # Rotate lại ảnh original (Nếu original image đang bị xoay 90, 180 hoặc 270)
    org_img, img = deskew(img, write_on_terminal=False)
    img = contrast_adjustment(img, write_on_terminal=False)
    img = remove_stamp(img, write_on_terminal=False)
    img = signature_remove(img, signature_logo_detection, cleaner, write_on_terminal=False)
    return org_img, img

def convert_image_to_base64(pil_img):
    img_byte_arr = io.BytesIO()
    pil_img.save(img_byte_arr, format='JPEG')
    img_byte_arr = img_byte_arr.getvalue()
    img_b64_string = b64encode(img_byte_arr).decode()
    img_b64_string = img_b64_string.replace('\n', '')
    img_b64_string = 'data:image/jpeg;base64,' + img_b64_string
    return img_b64_string

# Convert pdf to list of images and preprocess
def convert_pdf2images_and_preprocess(pdf, signature_logo_detection, cleaner, return_type):
    # # PDF to images sử dụng thư viện pdf2image
    # print('CONVERT_PDF2IMAGES')
    # images = convert_from_bytes(pdf)
    # base64_images = []
    # print('PREPROCESS IMAGES')
    # for image in tqdm(images):
    #     # Make copy and preprocess image
    #     image_array = np.array(image)
    #     image_array = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR) # convert RGB to BGR since preprocess is used OpenCV image format
    #     org_image_array, preprocess_image_array = preprocess_image(image_array, signature_logo_detection, cleaner)
        
    #     preprocess_image_array = cv2.cvtColor(preprocess_image_array, cv2.COLOR_BGR2RGB) # reconvert BGR to RGB
    #     org_image_array = cv2.cvtColor(org_image_array, cv2.COLOR_BGR2RGB) # reconvert BGR to RGB
        
    #     preprocess_image_pil = Image.fromarray(preprocess_image_array.astype('uint8')).convert('RGB')
    #     org_image_pil = Image.fromarray(org_image_array.astype('uint8')).convert('RGB')
        
    #     base64_images.append({'original': convert_image_to_base64(org_image_pil), 'preprocess': convert_image_to_base64(preprocess_image_pil)})

    # return base64_images

    # pdf to images sử dụng thư viện pymupdf
    print('CONVERT_PDF2IMAGES AND PREPROCESS')
    base64_images = []
    doc = fitz.open("pdf", pdf)
    zoom = 2
    mat = fitz.Matrix(zoom, zoom)
    count = 0
    # Count variable is to get the number of pages in the pdf
    for p in doc:
        count += 1
    for i in tqdm(range(count)):
        page = doc.load_page(i)
        pix = page.get_pixmap(matrix=mat)
        data = pix.pil_tobytes(format="jpeg", optimize=True)
        image = Image.open(io.BytesIO(data))
        # Make copy and preprocess image
        image_array = np.array(image)
        image_array = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR) # convert RGB to BGR since preprocess is used OpenCV image format
        org_image_array, preprocess_image_array = preprocess_image(image_array, signature_logo_detection, cleaner)
        
        if return_type=='base64':
            preprocess_image_array = cv2.cvtColor(preprocess_image_array, cv2.COLOR_BGR2RGB) # reconvert BGR to RGB
            org_image_array = cv2.cvtColor(org_image_array, cv2.COLOR_BGR2RGB) # reconvert BGR to RGB
            
            preprocess_image_pil = Image.fromarray(preprocess_image_array.astype('uint8')).convert('RGB')
            org_image_pil = Image.fromarray(org_image_array.astype('uint8')).convert('RGB')
            
            base64_images.append({'original': convert_image_to_base64(org_image_pil), 'preprocess': convert_image_to_base64(preprocess_image_pil)})
        elif return_type=='image':
            base64_images.append(preprocess_image_array)

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