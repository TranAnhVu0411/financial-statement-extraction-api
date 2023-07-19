from .test import PreprocessApi, OCRApi, End2EndOCRApi

def initialize_routes(api):
    api.add_resource(PreprocessApi, '/api/preprocess')
    api.add_resource(OCRApi, '/api/ocr')
    api.add_resource(End2EndOCRApi, '/api/e2eocr')