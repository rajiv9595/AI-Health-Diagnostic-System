"""
Database models for the AI Health Diagnostic System
"""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import json

db = SQLAlchemy()


class User(db.Model):
    """User model for authentication"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='patient')  # 'patient' or 'doctor'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    patient_profile = db.relationship('Patient', backref='user', uselist=False, cascade='all, delete-orphan')
    doctor_profile = db.relationship('Doctor', backref='user', uselist=False, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password against hash"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'email': self.email,
            'role': self.role,
            'created_at': self.created_at.isoformat()
        }


class Patient(db.Model):
    """Patient profile model"""
    __tablename__ = 'patients'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    full_name = db.Column(db.String(100), nullable=False)
    date_of_birth = db.Column(db.Date)
    gender = db.Column(db.String(10))
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    medical_history = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    xray_reports = db.relationship('XRayReport', backref='patient', lazy='dynamic', cascade='all, delete-orphan')
    symptom_checks = db.relationship('SymptomCheck', backref='patient', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'full_name': self.full_name,
            'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'gender': self.gender,
            'phone': self.phone,
            'address': self.address,
            'medical_history': self.medical_history,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class Doctor(db.Model):
    """Doctor profile model"""
    __tablename__ = 'doctors'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    full_name = db.Column(db.String(100), nullable=False)
    specialization = db.Column(db.String(100))
    license_number = db.Column(db.String(50), unique=True)
    phone = db.Column(db.String(20))
    hospital = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'full_name': self.full_name,
            'specialization': self.specialization,
            'license_number': self.license_number,
            'phone': self.phone,
            'hospital': self.hospital,
            'created_at': self.created_at.isoformat()
        }


class XRayReport(db.Model):
    """X-ray analysis report model"""
    __tablename__ = 'xray_reports'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    image_path = db.Column(db.String(255), nullable=False)
    gradcam_path = db.Column(db.String(255))
    
    # Predictions (stored as JSON string)
    predictions = db.Column(db.Text, nullable=False)  # JSON: {"Normal": 0.1, "Pneumonia": 0.7, ...}
    predicted_class = db.Column(db.String(50), nullable=False)
    confidence = db.Column(db.Float, nullable=False)
    
    # Additional info
    notes = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')  # pending, reviewed, urgent
    reviewed_by = db.Column(db.Integer, db.ForeignKey('doctors.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def get_predictions(self):
        """Parse predictions JSON"""
        return json.loads(self.predictions) if self.predictions else {}
    
    def set_predictions(self, pred_dict):
        """Set predictions from dictionary"""
        self.predictions = json.dumps(pred_dict)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'image_path': self.image_path,
            'gradcam_path': self.gradcam_path,
            'predictions': self.get_predictions(),
            'predicted_class': self.predicted_class,
            'confidence': self.confidence,
            'notes': self.notes,
            'status': self.status,
            'reviewed_by': self.reviewed_by,
            'created_at': self.created_at.isoformat()
        }


class SymptomCheck(db.Model):
    """Symptom checker history model"""
    __tablename__ = 'symptom_checks'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    symptoms = db.Column(db.Text, nullable=False)  # Comma-separated symptoms
    
    # Predictions
    predicted_disease = db.Column(db.String(100), nullable=False)
    confidence = db.Column(db.Float, nullable=False)
    urgency_level = db.Column(db.String(20), nullable=False)  # mild, moderate, severe
    
    # Top 3 predictions (stored as JSON)
    top_predictions = db.Column(db.Text)  # JSON: [{"disease": "...", "confidence": 0.8}, ...]
    
    # Recommendations
    recommendations = db.Column(db.Text)
    status = db.Column(db.String(20), default='active')  # active, resolved
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def get_top_predictions(self):
        """Parse top predictions JSON"""
        return json.loads(self.top_predictions) if self.top_predictions else []
    
    def set_top_predictions(self, pred_list):
        """Set top predictions from list"""
        self.top_predictions = json.dumps(pred_list)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'symptoms': self.symptoms,
            'predicted_disease': self.predicted_disease,
            'confidence': self.confidence,
            'urgency_level': self.urgency_level,
            'top_predictions': self.get_top_predictions(),
            'recommendations': self.recommendations,
            'status': self.status,
            'created_at': self.created_at.isoformat()
        }


class Alert(db.Model):
    """Alert model for urgent cases"""
    __tablename__ = 'alerts'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    alert_type = db.Column(db.String(20), nullable=False)  # xray, symptom
    reference_id = db.Column(db.Integer, nullable=False)  # ID of XRayReport or SymptomCheck
    message = db.Column(db.Text, nullable=False)
    severity = db.Column(db.String(20), nullable=False)  # low, medium, high, critical
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'alert_type': self.alert_type,
            'reference_id': self.reference_id,
            'message': self.message,
            'severity': self.severity,
            'is_read': self.is_read,
            'created_at': self.created_at.isoformat()
        }










