import cv2

# Get text region bounding box
def text_region_detection(img_array, blur_kernel = (7,7), dilate_kernel = (5,4)):
    # Load image, grayscale, Gaussian blur, Otsu's threshold
    gray = cv2.cvtColor(img_array, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, blur_kernel, 0)
    thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

    # Create rectangular structuring element and dilate
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, dilate_kernel)
    dilate = cv2.dilate(thresh, kernel, iterations=5)

    # Find contours and draw rectangle
    cnts = cv2.findContours(dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]
    metadata = []
    for c in enumerate(cnts):
        x,y,w,h = cv2.boundingRect(c[1])
        metadata.append({'text-region': (x, y, w, h)})
    return metadata

# Preprocess text line before OCR (remove white space in left and right around line)
def preprocess_line_region(line, blur_kernel = (7,7), dilate_kernel = (7,7)):
    # Load image, grayscale, Gaussian blur, Otsu's threshold
    gray = cv2.cvtColor(line, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, blur_kernel, 0)
    thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

    # Create rectangular structuring element and dilate
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, dilate_kernel)
    dilate = cv2.dilate(thresh, kernel, iterations=5)

    # Find contours and draw rectangle
    cnts = cv2.findContours(dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]
    min_x_list = []
    max_x_list = []
    for c in enumerate(cnts):
        x,_,w,_ = cv2.boundingRect(c[1])
        min_x_list.append(x)
        max_x_list.append(x+w)
    return min(min_x_list), max(max_x_list)