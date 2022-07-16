import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    # Web form security
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'

    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # PDF folder
    PDF_FOLDER_PATH = os.environ.get('PDF_FOLDER_PATH') or os.path.join(basedir, 'pdf')

    # Questions per page
    QUESTIONS_PER_PAGE = int(os.environ.get('QUESTIONS_PER_PAGE')) or 10

    # Twilio Verify
    TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
    TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
    TWILIO_VERIFY_SERVICE_ID = os.environ.get('TWILIO_VERIFY_SERVICE_ID')
