from flask import Response, request, jsonify, make_response
from flask_restful import Resource
from ocr.preprocess import convert_pdf2images_and_preprocess, table_text_seperator
import cv2
import numpy as np
from ocr.ocr_text import ocr_text
from ocr.ocr_table import ocr_table
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
        image_metadata = convert_pdf2images_and_preprocess(response, signature_logo_detection, cleaner)
        return make_response(image_metadata, 200)
        
class OCRApi(Resource):
    def post(self):
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
                table_structure = ocr_table(table['image'], tsr_model, net, detector, id)
                tables_metadata.append({'table_coordinate': table['table_coordinate'], 'table_structure': table_structure})
        return make_response({'metadata': {'text_metadata': text_metadata, 'table_metadata': tables_metadata}}, 200)

        
        
    