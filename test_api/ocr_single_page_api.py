import requests
import os
import time

def ocr_single(image_path, url, export_type):
    # Thay đổi payload
    # Nếu muốn lấy luckysheet data => sử dụng 'app'
    # Nếu muốn lấy toạ độ text line trong các cell => sử dụng metadata
    # Nếu muốn lấy base64 excel file => sử dụng file
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
    image_path = "/Users/trananhvu/Documents/GitHub/test/example/images/test1/preprocess/4.jpg"
    export_type = 'app'
    result = ocr_single(image_path, url, export_type)

    print("RESULT")
    print(result)