import base64
from PIL import Image
from openpyxl import load_workbook
import io
import os

def b64_to_image(base64_string, path):
    # base 64 string đang để dưới dạng data:image/jpeg;base64, {encoded_data}
    # Chỉ cần quan tâm đến encoded_data
    _, encoded_data = base64_string.split(",", 1)
    imgdata = base64.b64decode(str(encoded_data))
    img = Image.open(io.BytesIO(imgdata))
    img.save(path)

def b64_to_excel(base64_string, path):
    _, encoded_data = base64_string.split(",", 1)
    # Decode the base64 data
    decoded_data = base64.b64decode(str(encoded_data))

    # Create a BytesIO object to read the decoded data
    excel_data = io.BytesIO(decoded_data)

    # Load the Excel file using openpyxl
    workbook = load_workbook(excel_data)

    workbook.save(path)

def create_dir(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)