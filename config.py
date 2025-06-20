import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'sua-chave-secreta-aqui'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///micro_erp.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False 