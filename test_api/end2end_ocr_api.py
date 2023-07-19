import requests
import os
from pathlib import Path
import base64
from tqdm import tqdm
from PIL import Image
import io
import time
from openpyxl import load_workbook
import json

def create_dir(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)


def b64_to_excel(base64_string, path):
    _, encoded_data = base64_string.split(",", 1)
    # Decode the base64 data
    decoded_data = base64.b64decode(str(encoded_data))

    # Create a BytesIO object to read the decoded data
    excel_data = io.BytesIO(decoded_data)

    # Load the Excel file using openpyxl
    workbook = load_workbook(excel_data)

    workbook.save(path)

if __name__ == "__main__":
    print("RUNNING REQUEST")
    url = "http://127.0.0.1:3502/api/e2eocr"
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
    save_dir = 'result/{}'.format(Path(pdf_path).stem)

    print("SAVING RESULTS...")
    for i, metadata in tqdm(enumerate(response.json())):
        create_dir(os.path.join(save_dir, str(i)))
        # Write text metadata
        with open(os.path.join(save_dir, str(i), 'text_metadata.json'), 'w') as f:
            json.dump(metadata['text_metadata'], f)
        # Write text
        txt_file = open(os.path.join(save_dir, str(i), 'text.txt'), "a")
        txt_file.write(metadata['text'])
        txt_file.close()
        # Write table
        if len(metadata['table_metadata'])!=0:
            for j, table in enumerate(metadata['table_metadata']):
                excel_path = os.path.join(save_dir, str(i), '{}.xlsx'.format(str(table['table_coordinate'])))
                b64_to_excel(table['excel_file'], excel_path)
        