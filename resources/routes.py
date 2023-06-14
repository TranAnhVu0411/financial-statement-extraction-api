from .test import PreprocessApi, OCRApi

def initialize_routes(api):
    api.add_resource(PreprocessApi, '/api/preprocess')
    api.add_resource(OCRApi, '/api/ocr')