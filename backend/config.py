import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'monify-verify-dev-secret')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///monify_verify.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Monnify
    MONNIFY_API_KEY = os.environ.get('MONNIFY_API_KEY', '')
    MONNIFY_SECRET_KEY = os.environ.get('MONNIFY_SECRET_KEY', '')
    MONNIFY_BASE_URL = os.environ.get('MONNIFY_BASE_URL', 'https://sandbox.monnify.com')
    MONNIFY_CONTRACT_CODE = os.environ.get('MONNIFY_CONTRACT_CODE', '')
    MONNIFY_WALLET_ACCOUNT = os.environ.get('MONNIFY_WALLET_ACCOUNT', '')

    # App
    BASE_URL = os.environ.get('BASE_URL', 'http://localhost:5000')
    QR_CODE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'qr_codes')
    UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
