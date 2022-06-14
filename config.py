import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    # Web form security
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'

    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
