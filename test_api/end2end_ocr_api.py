import requests
import os
from pathlib import Path
from tqdm import tqdm
import argparse
import time
import json
from utils import create_dir, b64_to_excel
import os
from dotenv import load_dotenv

parser = argparse.ArgumentParser(description='End to End OCR')
parser.add_argument('-file_path', '--file_path', type=str, help='pdf file path', required=True)
args = parser.parse_args()

if __name__ == "__main__":
    load_dotenv()
    print("RUNNING REQUEST")
    url = "http://127.0.0.1:{}/api/e2eocr".format(os.getenv('PORT'))
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
    save_dir = os.path.join('example', 'result', Path(pdf_path).stem)

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
        