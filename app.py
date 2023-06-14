from flask import Flask
from flask_restful import Api
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

from resources.routes import initialize_routes
api = Api(app)
initialize_routes(api)