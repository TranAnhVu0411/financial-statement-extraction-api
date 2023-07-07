import requests
import os
from pathlib import Path
import base64
from tqdm import tqdm
from PIL import Image
import io
import time

def b64_to_image(base64_string, path):
    # base 64 string đang để dưới dạng data:image/jpeg;base64, {encoded_data}
    # Chỉ cần quan tâm đến encoded_data
    _, encoded_data = base64_string.split(",", 1)
    imgdata = base64.b64decode(str(encoded_data))
    img = Image.open(io.BytesIO(imgdata))
    img.save(path)

def create_dir(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)

if __name__ == "__main__":
    print("RUNNING REQUEST")
    url = "http://localhost:3502/api/preprocess"
    pdf_path = "/Users/trananhvu/Downloads/test1.pdf"
    payload={}
    files=[
        ('file',(os.path.basename(pdf_path),open(pdf_path,'rb'),'application/pdf'))
    ]
    headers = {}
    start = time.perf_counter()
    response = requests.request("POST", url, headers=headers, data=payload, files=files)
    request_time = time.perf_counter() - start
    print("REQUEST RUNTIME: {}".format(request_time))

    print("CREATING RESULT DIR")
    original_save_dir = 'example/images/{}/original'.format(Path(pdf_path).stem)
    preprocess_save_dir = 'example/images/{}/preprocess'.format(Path(pdf_path).stem)
    create_dir(os.path.join(original_save_dir))
    create_dir(os.path.join(preprocess_save_dir))

    print("SAVING RESULTS...")
    for i, images in tqdm(enumerate(response.json())):
        filename = '{}.jpg'.format(i)
        b64_to_image(images['original'], os.path.join(original_save_dir, filename))
        b64_to_image(images['preprocess'], os.path.join(preprocess_save_dir, filename))