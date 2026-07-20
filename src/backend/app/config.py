import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '../../../.env'))
project_root = os.path.abspath(os.path.join(basedir, '../../..'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
    DATABASE_URL = os.environ.get('DATABASE_URL')
    UPLOADED_FRAMES_DIR = os.path.join(project_root, 'uploaded_frames')
