from ocr_single_page_api import ocr_single
from utils import create_dir
import os
import json
import argparse

parser = argparse.ArgumentParser(description='OCR PDF')
parser.add_argument('-file_path', '--file_path', type=str, help='preprocess image dir', required=True)
parser.add_argument('-type', '--type', type=str, help='export type', choices=['app', 'test'], default='app')
args = parser.parse_args()

if __name__ == "__main__":
    url = "http://localhost:3502/api/ocr"
    export_type = args.type
    preprocess_img_dir = args.file_path
    pdf_name = os.path.normpath(preprocess_img_dir).split(os.path.sep)[-2] 
    save_dir = os.path.join('example', 'metadata', pdf_name)
    create_dir(save_dir)

    for idx, img_name in enumerate(os.listdir(preprocess_img_dir)):
        print('PAGE {}'.format(idx))
        result = ocr_single(os.path.join(preprocess_img_dir, img_name), url, export_type)
        with open(os.path.join(save_dir, '{}.json'.format(idx)), 'w') as f:
            json.dump(result, f)