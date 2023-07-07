import requests
import os
import time

def ocr_single(image_path, url):
    payload={}
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
    result = ocr_single(image_path, url)

    print("RESULT")
    print(result)