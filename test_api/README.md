# test_api

Thư mục kiểm thử API, gồm các file:
- preprocess_api: Kiểm thử api tiền xử lý. Đầu ra: Trong folder example/images/{tên pdf}
    - folder original: Chứa danh sách các ảnh gốc được trích xuất từ PDF
    - folder preprocess: Chứa danh sách các ảnh đã qua tiền xử lý

- ocr_single_api: Kiểm thử api OCR ứng với 1 ảnh. Đầu ra: in ra kết quả metadata OCR

- ocr_pdf_api: Kiểm thử api OCR ứng với tập hợp tất cả các ảnh đã qua tiền xử lý (cần output của preprocess_api.py). Đầu ra: Trong folder example/metadata/{tên pdf} là danh sách file json chứa thông tin OCR metadata

- end2end_ocr_api: Chạy OCR file PDF từ bước tiền xử lý đến bước trả ra kết quả đầu ra (Trong folder example/result/{tên pdf})

Để chạy được: 
- Điều hướng vào thư mục test_api (cd test_api)
- Chạy các file tương ứng, với các đầu vào sau:
    - preprcess_api: python preprocess_api.py --file_path={PDF file path}
    - ocr_single_api: python ocr_single_api.py --file_path={Image file path} --type={app hoặc test}
    - ocr_pdf_api: python ocr_pdf_api.py --file_path={Preprocess images folder directory} --type={app hoặc test}
    - end2end_ocr_api: python ocr_pdf_api.py --file_path={PDF file path}

Trong đó:
- type = app => Trong metadata OCR, table_structure trả về cấu trúc dữ liệu luckysheet
- type = test => Trong metadata OCR, table_structure trả về cấu trúc dữ liệu cell, gồm vị trí của cell trong bảng, cũng như toạ độ và text tương ứng của text region và text line trong cell