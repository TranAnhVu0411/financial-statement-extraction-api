# test_api

Thư mục kiểm thử API, gồm các file:
- preprocess_api.py: Kiểm thử api tiền xử lý, gồm 2 input:
    - url: url của API (/api/preprocess)
    - pdf_path: đường dẫn của file PDF
    Đầu ra: Trong folder example/images/{tên pdf}
    - folder original: Chứa danh sách các ảnh gốc được trích xuất từ PDF
    - folder preprocess: Chứa danh sách các ảnh đã qua tiền xử lý

- ocr_single_api.py: Kiểm thử api OCR ứng với 1 ảnh, gồm 2 input:
    - url: url của API (/api/ocr)
    - image_path: đướng dẫn của ảnh trang
    Đầu ra: in ra kết quả metadata OCR

- ocr_pdf_api: Kiểm thử api OCR ứng với tập hợp tất cả các ảnh đã qua tiền xử lý (cần output của preprocess_api.py), gồm 3 input:
    - url: url của API (/api/ocr)
    - preprocess_img_dir: đường dẫn của thư mục chứa ảnh đã tiền xử lý (example/images/{tên pdf}/preprocess)
    - save_dir: đường dẫn của thư mục lưu (example/metadata/{tên pdf}/)
    Đầu ra: Trong folder example/metadata/{tên pdf} là danh sách file json chứa thông tin OCR metadata

Để chạy được: 
- Điều hướng vào thư mục test_api (cd test_api)
- Thay đổi input cho phù hợp
- Chạy python {tên file}.py