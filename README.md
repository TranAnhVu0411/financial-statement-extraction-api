# financial-statement-extraction-api

## I, Giới thiệu về các API
Cung cấp 2 API (cổng 3502):
- /api/preprocess:
    - Đầu vào: file PDF
    - Đầu ra: Danh sách thông tin ảnh trang trích xuất của PDF, thông tin ảnh bao gồm ảnh gốc (original) và ảnh tiền xử lý (preprocess) được để dưới dạng base64
- /api/ocr:
    - Đầu vào: 1 ảnh trang đã tiền xử lý và loại table metadata sẽ xuất ra (type):
    - Đầu ra: Metadata OCR của ảnh trang đó, bao gồm:
        - Thông tin của các bảng gồm vị trí của bảng và metadata của bảng (tuỳ thuộc vào type, tham khảo trong example/README.md)
        - Thông tin của các đoạn văn gồm danh sách thông tin các dòng trong đoạn văn, thông tin các dòng trong đoạn văn bao gồm vị trí của dòng và text tương ứng với dòng đó

## II, Hướng dẫn cài đặt
- Cài tesseract (trên linux server dùng lệnh sudo yum install tesseract), tải osd.traineddata (Tham khảo https://stackoverflow.com/questions/14800730/tesseract-running-error)
- ~~Cài poppler~~
- Cài ImageMagick (trên linux server dùng lệnh sudo yum install ImageMagick)
- Clone git repository
- Vào https://drive.google.com/drive/folders/15u27iYPSYJDOIJq_vMoMxs6_7yVpybFM?usp=sharing tải pretrained models, trong drive có 2 folders, hướng dẫn tải:
    - models: tải folder về và chuyển folder vào thư mục financial-statement-extraction-api
    - ~~signver: trong signver có folder models, tải folder models và chuyển folder vào thư mục financial-statement-extraction-api/signver~~
    - gan_files: trong gan_files có folder checkpoints, tải folder checkpoints và chuyển folder vào thư mục financial-statement-extraction-api/ocr/gan_files
- Vào terminal, điều hướng vào thư mục bằng cd financial-statement-extraction-api
- Tạo Virtual Environment và kích hoạt môi trường: python3 -m venv venv => source venv/bin/activate (Python 3.9.16)
- Tạo file .env, thay đổi PORT và đường dẫn làm việc như trong .env_copy
- Chạy pip install -r requirements.txt để tải các thư viện về
- Chạy lệnh python run.py để chạy server
- Có thể chạy API bằng postman hoặc vào thư mục test_api (cd test_api) và chạy các ví dụ trong đó để có kết quả hiển thị trong folder example