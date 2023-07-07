from ocr_single_page_api import ocr_single
from preprocess_api import create_dir
import os
import json

if __name__ == "__main__":
    url = "http://localhost:3502/api/ocr"
    preprocess_img_dir = 'example/images/test1/preprocess'
    save_dir = 'example/metadata/test1'
    create_dir(save_dir)

    for idx, img_name in enumerate(os.listdir(preprocess_img_dir)):
        print('PAGE {}'.format(idx))
        result = ocr_single(os.path.join(preprocess_img_dir, img_name), url)
        with open(os.path.join(save_dir, '{}.json'.format(idx)), 'w') as f:
            json.dump(result, f)