import os
from dotenv import load_dotenv
from datetime import timedelta


basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'), override=True)

# creating a configuration class
class Config(object):
    MONGO_URI =  os.environ.get('MONGO_URI')
    EMAIL_USERNAME = os.environ.get('EMAIL_USERNAME')
    EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD')
    SMTP_SERVER = os.environ.get('SMTP_SERVER')
    SMTP_PORT = os.environ.get('SMTP_PORT')
    IMAGE_URL = os.environ.get('IMAGE_URL')
    LECTURER_IMAGE_URL = os.environ.get('LECTURER_IMAGE_URL')