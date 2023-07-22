import requests
import os
from pathlib import Path
from tqdm import tqdm
import time
import argparse
from utils import create_dir, b64_to_image

parser = argparse.ArgumentParser(description='Preprocess page images')
parser.add_argument('file_path', type=str, help='pdf file path', required=True)
args = parser.parse_args()

if __name__ == "__main__":
    print("RUNNING REQUEST")
    url = "http://127.0.0.1:3502/api/preprocess"
    pdf_path = args.file_path
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
    original_save_dir = os.path.join('example', 'images', Path(pdf_path).stem, 'original')
    preprocess_save_dir = os.path.join('example', 'images', Path(pdf_path).stem, 'preprocess')
    create_dir(os.path.join(original_save_dir))
    create_dir(os.path.join(preprocess_save_dir))

    print("SAVING RESULTS...")
    for i, images in tqdm(enumerate(response.json())):
        filename = '{}.jpg'.format(i)
        b64_to_image(images['original'], os.path.join(original_save_dir, filename))
        b64_to_image(images['preprocess'], os.path.join(preprocess_save_dir, filename))