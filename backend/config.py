"""
Configuration settings for the AI Health Diagnostic System
"""
import os
from datetime import timedelta
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


class Config:
    """Base configuration"""
    
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'health_diagnostic.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key-change-in-production'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # File Upload
    UPLOAD_FOLDER = os.path.join(basedir, 'uploads')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'dcm'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    
    # Model Paths
    MODELS_FOLDER = os.path.join(basedir, 'saved_models')
    XRAY_MODEL_PATH = os.path.join(MODELS_FOLDER, 'xray_model.keras')
    SYMPTOM_MODEL_PATH = os.path.join(MODELS_FOLDER, 'symptom_model.pkl')
    SYMPTOM_VECTORIZER_PATH = os.path.join(MODELS_FOLDER, 'symptom_vectorizer.pkl')
    SYMPTOM_ENCODER_PATH = os.path.join(MODELS_FOLDER, 'symptom_label_encoder.pkl')
    
    # Grad-CAM Settings
    GRADCAM_LAYER = 'conv5_block16_concat'  # For DenseNet121
    
    # Disease Categories
    XRAY_CLASSES = ['Normal', 'Pneumonia', 'Tuberculosis', 'COVID-19']
    
    # Gemini Settings
    GEMINI_MODEL = "gemini-2.5-flash"
    
    # Urgency Levels
    URGENCY_LEVELS = {
        'mild': ['Common Cold', 'Allergy', 'Migraine'],
        'moderate': ['Gastroenteritis', 'Bronchitis', 'Urinary tract infection'],
        'severe': ['Pneumonia', 'COVID-19', 'Heart Attack', 'Stroke', 'Tuberculosis']
    }
    
    # CORS
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*').split(',')


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    FLASK_ENV = 'development'


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    FLASK_ENV = 'production'


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

