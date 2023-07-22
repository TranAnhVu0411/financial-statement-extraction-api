from flask import Response, request, jsonify, make_response
from flask_restful import Resource
from ocr.preprocess import convert_pdf2images_and_preprocess, table_text_seperator
import cv2
import numpy as np
from ocr.ocr_text import ocr_text, metadata_to_text
from ocr.ocr_table import ocr_table_app, ocr_table_file, ocr_table_metadata
from ocr.model import *

class PreprocessApi(Resource):
    def post(self):
        if 'file' not in request.files:
            return make_response("No file part", 400)
        file = request.files['file']
        if file.filename == '':
            return make_response("No selected file", 400)
        if file.mimetype!='application/pdf':
            return make_response("Upload file format is not correct", 400)
        response = file.read()
        image_metadata = convert_pdf2images_and_preprocess(response, signature_logo_detection, cleaner, return_type='base64')
        return make_response(image_metadata, 200)
        
class OCRApi(Resource):
    def post(self):
        if 'type' not in request.form:
            return make_response("No type part", 400)
        if 'file' not in request.files:
            return make_response("No file part", 400)
        file = request.files['file']
        if file.filename == '':
            return make_response("No selected file", 400)
        if file.mimetype!='image/jpeg':
            return make_response("Upload file format is not correct", 400)
        response = file.read()
        img = cv2.imdecode(np.fromstring(response, np.uint8), cv2.IMREAD_COLOR)
        results = table_text_seperator(img, table_detection)
        text_metadata = ocr_text(results['text'], detector, net)
        tables_metadata = []
        if len(results['tables']) != 0:
            for table in results['tables']:
                # trả về luckysheet table structure (Cho frontend)
                if request.form['type'] == 'app':
                    table_structure = ocr_table_app(table['image'], tsr_model, net, detector)
                    tables_metadata.append({'table_coordinate': table['table_coordinate'], 'table_structure': table_structure})
                # trả về table structure với thông tin text cell chứa metadata của text_region và line_region
                if request.form['type'] == 'test':
                    table_metadata = ocr_table_metadata(table['image'], tsr_model, net, detector)
                    tables_metadata.append({'table_coordinate': table['table_coordinate'], 'table_metadata': table_metadata})

        return make_response({'metadata': {'text_metadata': text_metadata, 'table_metadata': tables_metadata}}, 200)

class End2EndOCRApi(Resource):
    def post(self):
        if 'file' not in request.files:
            return make_response("No file part", 400)
        file = request.files['file']
        if file.filename == '':
            return make_response("No selected file", 400)
        if file.mimetype!='application/pdf':
            return make_response("Upload file format is not correct", 400)
        response = file.read()
        images = convert_pdf2images_and_preprocess(response, signature_logo_detection, cleaner, return_type='image')
        page_results = []
        for idx, img in enumerate(images):
            print('Page {}'.format(idx))
            results = table_text_seperator(img, table_detection)
            text_metadata = ocr_text(results['text'], detector, net)
            text = metadata_to_text(text_metadata)
            tables_metadata = []
            if len(results['tables']) != 0:
                for table in results['tables']:
                    table_base64 = ocr_table_file(table['image'], tsr_model, net, detector)
                    tables_metadata.append({'table_coordinate': table['table_coordinate'], 'excel_file': table_base64})
            page_results.append({'text_metadata': text_metadata, 'text': text, 'table_metadata': tables_metadata})

        return make_response(page_results, 200)
        
    