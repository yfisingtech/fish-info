import os
from dotenv import load_dotenv

class Config(object):
    load_dotenv()
    UPLOAD_FOLDER = 'uploads/'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
    GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')
    OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY')
    NOTION_API_KEY = os.getenv('NOTION_API_KEY')
