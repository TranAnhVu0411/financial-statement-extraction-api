from app import app
import os
from dotenv import load_dotenv

load_dotenv()
app.run(port=os.getenv('PORT'), debug=True, host = '0.0.0.0')