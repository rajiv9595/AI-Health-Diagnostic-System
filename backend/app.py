"""
Main Flask Application for AI Health Diagnostic System
"""
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
import os

from config import config
from models.database import db
from routes.auth import auth_bp
from routes.xray import xray_bp
from routes.symptoms import symptoms_bp
from routes.dashboard import dashboard_bp


def create_app(config_name='development'):
    """
    Application factory pattern
    
    Args:
        config_name: Configuration name (development/production/testing)
        
    Returns:
        Flask application instance
    """
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": app.config['CORS_ORIGINS']}})
    jwt = JWTManager(app)
    Migrate(app, db)
    
    # JWT error handlers
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        print(f"Invalid token error: {error}")
        return jsonify({'error': 'Invalid token', 'message': str(error)}), 422
    
    @jwt.unauthorized_loader
    def unauthorized_callback(error):
        print(f"Unauthorized error: {error}")
        return jsonify({'error': 'Missing authorization header', 'message': str(error)}), 401
    
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_data):
        print(f"Expired token")
        return jsonify({'error': 'Token has expired'}), 401
    
    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_data):
        print(f"Revoked token")
        return jsonify({'error': 'Token has been revoked'}), 401
    
    # Create upload folders
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['MODELS_FOLDER'], exist_ok=True)
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'xrays'), exist_ok=True)
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'gradcam'), exist_ok=True)
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(xray_bp, url_prefix='/api/xray')
    app.register_blueprint(symptoms_bp, url_prefix='/api/symptoms')
    app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not found'}), 404
    
    @app.errorhandler(422)
    def unprocessable(error):
        print(f"422 Error: {error}")
        return jsonify({'error': 'Unprocessable entity', 'message': str(error)}), 422
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        print(f"500 Error: {error}")
        return jsonify({'error': 'Internal server error'}), 500
    
    # Health check endpoint
    @app.route('/api/health')
    def health_check():
        return jsonify({
            'status': 'healthy',
            'message': 'AI Health Diagnostic System API is running'
        })
    
    # Create database tables
    with app.app_context():
        db.create_all()
        
        # Create default users if they don't exist
        from models.database import User, Patient, Doctor
        
        # Create default doctor
        doctor_user = User.query.filter_by(email='doctor@hospital.com').first()
        if not doctor_user:
            doctor_user = User(email='doctor@hospital.com', role='doctor')
            doctor_user.set_password('doctor123')
            db.session.add(doctor_user)
            db.session.commit()  # Commit user first
            
            doctor_profile = Doctor(
                user_id=doctor_user.id,
                full_name='Dr. Sarah Johnson',
                specialization='Radiology',
                license_number='MD-12345',
                phone='555-0101',
                hospital='City General Hospital'
            )
            db.session.add(doctor_profile)
            db.session.commit()  # Commit doctor profile
        
        # Create default patient
        patient_user = User.query.filter_by(email='patient@email.com').first()
        if not patient_user:
            patient_user = User(email='patient@email.com', role='patient')
            patient_user.set_password('patient123')
            db.session.add(patient_user)
            db.session.commit()  # Commit user first
            
            patient_profile = Patient(
                user_id=patient_user.id,
                full_name='John Doe',
                gender='Male',
                phone='555-0102',
                address='123 Main St, City, State'
            )
            db.session.add(patient_profile)
            db.session.commit()  # Commit patient profile
        
        print("Database initialized with default users")
    
    return app

# Create app instance for Gunicorn/Production
# This allows 'gunicorn app:app' to work
app = create_app(os.getenv('FLASK_ENV', 'production'))

if __name__ == '__main__':
    # When running directly (local dev), used debug mode
    print("\n" + "="*60)
    print("🩺 AI Health Diagnostic System - Backend API")
    print("="*60)
    print("\nDefault Credentials:")
    print("  Doctor:  doctor@hospital.com / doctor123")
    print("  Patient: patient@email.com / patient123")
    print("\nAPI running at: http://localhost:5000")
    print("Health check: http://localhost:5000/api/health")
    print("="*60 + "\n")
    
    app.run(host='0.0.0.0', port=5000, debug=True)

