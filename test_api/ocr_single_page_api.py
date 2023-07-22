import requests
import os
import time
import argparse

parser = argparse.ArgumentParser(description='OCR pdf')
parser.add_argument('-file_path', '--file_path', type=str, help='preprocess image', required=True)
parser.add_argument('-type', '--type', type=str, help='export type', choices=['app', 'test'], default='app')
args = parser.parse_args()

def ocr_single(image_path, url, export_type):
    payload={'type': export_type}
    files=[
        ('file',(os.path.basename(image_path),open(image_path,'rb'),'image/jpeg'))
    ]
    headers = {}
    start = time.perf_counter()
    response = requests.request("POST", url, headers=headers, data=payload, files=files)
    request_time = time.perf_counter() - start
    print("REQUEST RUNTIME: {}".format(request_time))
    return response.json()

if __name__ == "__main__":
    print("RUNNING REQUEST")
    url = "http://localhost:3502/api/ocr"
    image_path = args.file_path
    export_type = args.type
    result = ocr_single(image_path, url, export_type)

    print("RESULT")
    print(result)