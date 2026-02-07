"""
Authentication Routes
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token, 
    create_refresh_token,
    jwt_required, 
    get_jwt_identity
)
from models.database import db, User, Patient, Doctor, XRayReport, SymptomCheck
from datetime import datetime

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['email', 'password', 'role', 'full_name']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing field: {field}'}), 400
        
        # Check if user exists
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already registered'}), 400
        
        # Validate role
        if data['role'] not in ['patient', 'doctor']:
            return jsonify({'error': 'Invalid role'}), 400
        
        # Create user
        user = User(
            email=data['email'],
            role=data['role']
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.flush()
        
        # Create profile based on role
        if data['role'] == 'patient':
            profile = Patient(
                user_id=user.id,
                full_name=data['full_name'],
                date_of_birth=datetime.strptime(data.get('date_of_birth'), '%Y-%m-%d').date() if data.get('date_of_birth') else None,
                gender=data.get('gender'),
                phone=data.get('phone'),
                address=data.get('address'),
                medical_history=data.get('medical_history')
            )
        else:
            profile = Doctor(
                user_id=user.id,
                full_name=data['full_name'],
                specialization=data.get('specialization'),
                license_number=data.get('license_number'),
                phone=data.get('phone'),
                hospital=data.get('hospital')
            )
        
        db.session.add(profile)
        db.session.commit()
        
        # Create tokens
        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))
        
        return jsonify({
            'message': 'User registered successfully',
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': {
                **user.to_dict(),
                'profile': profile.to_dict()
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """User login"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password required'}), 400
        
        # Find user
        user = User.query.filter_by(email=data['email']).first()
        
        if not user or not user.check_password(data['password']):
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Get profile
        if user.role == 'patient':
            profile = Patient.query.filter_by(user_id=user.id).first()
        else:
            profile = Doctor.query.filter_by(user_id=user.id).first()
        
        # Create tokens
        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))
        
        return jsonify({
            'message': 'Login successful',
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': {
                **user.to_dict(),
                'profile': profile.to_dict() if profile else None
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get user profile"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get profile
        if user.role == 'patient':
            profile = Patient.query.filter_by(user_id=user.id).first()
            # Compute health score and tip
            health_score = 80
            if profile:
                from datetime import timedelta
                cutoff = datetime.utcnow() - timedelta(days=30)
                xrays = XRayReport.query.filter_by(patient_id=profile.id).filter(XRayReport.created_at >= cutoff).all()
                symptoms = SymptomCheck.query.filter_by(patient_id=profile.id).filter(SymptomCheck.created_at >= cutoff).all()
                for r in xrays:
                    if r.predicted_class != 'Normal':
                        health_score -= 10 if r.confidence < 0.8 else 15
                    else:
                        health_score += 2
                for s in symptoms:
                    if s.urgency_level == 'severe':
                        health_score -= 15
                    elif s.urgency_level == 'moderate':
                        health_score -= 7
                    else:
                        health_score += 2
                health_score = max(0, min(100, health_score))
            # Age-based friendly tip
            tip = None
            if profile and profile.date_of_birth:
                age = (datetime.utcnow().date() - profile.date_of_birth).days // 365
                if age >= 65:
                    tip = "You're doing great! Consider regular check-ups, light exercise, and staying hydrated. Wishing you good health!"
            extra = { 'health_score': health_score, 'health_tip': tip }
        else:
            profile = Doctor.query.filter_by(user_id=user.id).first()
            extra = {}
        
        return jsonify({
            'user': {
                **user.to_dict(),
                'profile': ({**profile.to_dict(), **extra} if profile else None)
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Update user profile"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        
        # Get profile
        if user.role == 'patient':
            profile = Patient.query.filter_by(user_id=user.id).first()
            
            # Update patient fields
            if 'full_name' in data:
                profile.full_name = data['full_name']
            if 'date_of_birth' in data:
                profile.date_of_birth = datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date()
            if 'gender' in data:
                profile.gender = data['gender']
            if 'phone' in data:
                profile.phone = data['phone']
            if 'address' in data:
                profile.address = data['address']
            if 'medical_history' in data:
                profile.medical_history = data['medical_history']
        else:
            profile = Doctor.query.filter_by(user_id=user.id).first()
            
            # Update doctor fields
            if 'full_name' in data:
                profile.full_name = data['full_name']
            if 'specialization' in data:
                profile.specialization = data['specialization']
            if 'phone' in data:
                profile.phone = data['phone']
            if 'hospital' in data:
                profile.hospital = data['hospital']
        
        profile.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Profile updated successfully',
            'profile': profile.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token"""
    try:
        user_id = get_jwt_identity()  # Already a string
        access_token = create_access_token(identity=user_id)
        
        return jsonify({
            'access_token': access_token
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

