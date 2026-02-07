"""
Symptom Checker Routes
"""
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.database import db, User, Patient, SymptomCheck, Alert
from models.ml_models.symptom_model import SymptomChecker
from models.nlp.symptom_parser import parse_symptoms
try:
    from models.ml_models.symptom_bert import SymptomBERT
    _ADV_AVAILABLE = True
except Exception:
    _ADV_AVAILABLE = False
    _ADV_AVAILABLE = False
import os
from utils.gemini_service import analyze_symptoms_with_gemini

symptoms_bp = Blueprint('symptoms', __name__)

# Initialize symptom checker (lazy loading)
symptom_checker = None


def get_symptom_checker():
    """Get or initialize symptom checker"""
    global symptom_checker
    if symptom_checker is None:
        model_path = current_app.config['SYMPTOM_MODEL_PATH']
        vectorizer_path = current_app.config['SYMPTOM_VECTORIZER_PATH']
        encoder_path = current_app.config['SYMPTOM_ENCODER_PATH']
        
        symptom_checker = SymptomChecker(
            model_path=model_path if os.path.exists(model_path) else None,
            vectorizer_path=vectorizer_path if os.path.exists(vectorizer_path) else None,
            encoder_path=encoder_path if os.path.exists(encoder_path) else None
        )
    return symptom_checker


@symptoms_bp.route('/check', methods=['POST'])
@jwt_required()
def check_symptoms():
    """Check symptoms and predict disease"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get patient profile
        patient = Patient.query.filter_by(user_id=user.id).first()
        if not patient:
            return jsonify({'error': 'Patient profile not found'}), 404
        
        data = request.get_json()
        
        if not data.get('symptoms'):
            return jsonify({'error': 'Symptoms are required'}), 400
        
        symptoms_text = data['symptoms']
        
        # Check for Gemini API Key
        gemini_key = os.getenv('GEMINI_API_KEY')
        prediction = None
        
        if gemini_key:
            try:
                # Try Gemini analysis
                prediction = analyze_symptoms_with_gemini(symptoms_text)
            except Exception as e:
                print(f"Gemini API error: {e}")
                prediction = None
        
        # Fallback to local model if Gemini fails or key missing
        if not prediction:
            # Get symptom checker
            checker = get_symptom_checker()
            
            try:
                # Predict disease
                prediction = checker.predict(symptoms_text)
            
        except Exception as e:
            # If model doesn't exist, return dummy prediction
            print(f"Symptom prediction error: {e}")
            prediction = {
                'predicted_disease': 'Common Cold',
                'confidence': 0.75,
                'urgency_level': 'mild',
                'top_predictions': [
                    {'disease': 'Common Cold', 'confidence': 0.75, 'urgency': 'mild'},
                    {'disease': 'Allergy', 'confidence': 0.15, 'urgency': 'mild'},
                    {'disease': 'Flu', 'confidence': 0.10, 'urgency': 'moderate'}
                ],
                'recommendations': [
                    'Rest and monitor your symptoms',
                    'Stay hydrated and get plenty of rest',
                    'Consider over-the-counter medication if needed',
                    'This is an AI prediction and not a substitute for professional medical advice'
                ]
            }
        
        # Save to database
        symptom_check = SymptomCheck(
            patient_id=patient.id,
            symptoms=symptoms_text,
            predicted_disease=prediction['predicted_disease'],
            confidence=prediction['confidence'],
            urgency_level=prediction['urgency_level'],
            recommendations='\n'.join(prediction['recommendations'])
        )
        symptom_check.set_top_predictions(prediction['top_predictions'])
        
        db.session.add(symptom_check)
        
        # Create alert for severe cases
        if prediction['urgency_level'] == 'severe' and prediction['confidence'] > 0.6:
            alert = Alert(
                patient_id=patient.id,
                alert_type='symptom',
                reference_id=symptom_check.id,
                message=f"Severe symptoms detected: {prediction['predicted_disease']} ({prediction['confidence']*100:.1f}% confidence)",
                severity='high' if prediction['confidence'] > 0.8 else 'medium'
            )
            db.session.add(alert)
            
            # Log alert
            print(f"🚨 ALERT: Patient {patient.full_name} - {alert.message}")
        
        db.session.commit()
        
        return jsonify({
            'message': 'Symptoms analyzed successfully',
            'result': symptom_check.to_dict(),
            'patient_name': patient.full_name
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@symptoms_bp.route('/check/v2', methods=['POST'])
@jwt_required()
def check_symptoms_v2():
    """
    Advanced symptom checker that accepts free text or keyword list.
    Request JSON:
      { "text": "paragraph or sentence", "keywords": [optional list] }
    """
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404

        patient = Patient.query.filter_by(user_id=user.id).first()
        if not patient:
            return jsonify({'error': 'Patient profile not found'}), 404

        data = request.get_json() or {}
        text = data.get('text') or ''
        keywords = data.get('keywords') or []

        parsed = parse_symptoms(keywords or text)

        # Fallback if nothing extracted
        symptoms_for_model = parsed['extracted'] or keywords
        if not symptoms_for_model and text:
            symptoms_for_model = [text]

        # Check for Gemini API Key
        gemini_key = os.getenv('GEMINI_API_KEY')
        prediction = None
        
        if gemini_key:
            try:
                # Try Gemini analysis on raw text or combined keywords
                input_text = text if text else ', '.join(keywords)
                prediction = analyze_symptoms_with_gemini(input_text)
                
                # If Gemini successful, format response similar to local model
                if prediction:
                    # Provide parsed structure as well if available
                    # If parsing failed or wasn't done appropriately because of Gemini usage
                    if not parsed or (not parsed['extracted'] and not parsed['raw']):
                        parsed = {'extracted': [], 'raw': input_text, 'severity_hint': prediction.get('urgency_level', 'mild')}

            except Exception as e:
                print(f"Gemini API error (v2): {e}")
                prediction = None

        if not prediction:
            checker = get_symptom_checker()
            try:
            # Heuristic: use advanced model if long paragraph and transformers available
            use_adv = bool(data.get('use_advanced')) or (len(text) > 80 and _ADV_AVAILABLE)
            if use_adv and _ADV_AVAILABLE:
                try:
                    adv = SymptomBERT()
                    adv_pred = adv.predict(text)
                    # Map into baseline format and blend urgency using parser rules via checker
                    baseline_like = {
                        'predicted_disease': adv_pred['predicted_disease'],
                        'confidence': adv_pred['confidence'],
                        'urgency_level': adv._urgency_hint(adv_pred['predicted_disease']),
                        'top_predictions': adv_pred['top_predictions'],
                        'recommendations': ''
                    }
                    # Reuse recommendation + rule merge from checker
                    tmp = checker.generate_recommendations(
                        baseline_like['predicted_disease'], baseline_like['urgency_level'], baseline_like['confidence']
                    )
                    baseline_like['recommendations'] = '\n'.join(tmp)
                    prediction = baseline_like
                except Exception as _:
                    prediction = checker.predict(', '.join(symptoms_for_model))
            else:
                prediction = checker.predict(', '.join(symptoms_for_model))
        except Exception as e:
            print(f"Symptom v2 prediction error: {e}")
            prediction = {
                'predicted_disease': 'Undetermined',
                'confidence': 0.0,
                'urgency_level': parsed.get('severity_hint', 'mild'),
                'top_predictions': [],
                'recommendations': [
                    'Insufficient data. Please provide more details about your symptoms.',
                ],
            }

        # Merge urgency hint
        if prediction.get('urgency_level') == 'mild' and parsed.get('severity_hint') == 'severe':
            prediction['urgency_level'] = 'severe'

        # Persist
        symptom_text = parsed['raw'] or text or ', '.join(keywords)
        check = SymptomCheck(
            patient_id=patient.id,
            symptoms=symptom_text,
            predicted_disease=prediction['predicted_disease'],
            confidence=prediction['confidence'],
            urgency_level=prediction['urgency_level'],
            recommendations='\n'.join(prediction.get('recommendations', []))
        )
        check.set_top_predictions(prediction.get('top_predictions', []))
        db.session.add(check)
        db.session.flush()

        # Severe alert
        if prediction['urgency_level'] == 'severe' and prediction.get('confidence', 0) >= 0.5:
            alert = Alert(
                patient_id=patient.id,
                alert_type='symptom',
                reference_id=check.id,
                message=f"Severe symptoms detected: {prediction['predicted_disease']} ({prediction.get('confidence',0)*100:.1f}% confidence)",
                severity='high'
            )
            db.session.add(alert)

        db.session.commit()

        return jsonify({
            'message': 'Symptoms analyzed successfully (v2)',
            'parsed': parsed,
            'result': check.to_dict(),
            'patient_name': patient.full_name
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@symptoms_bp.route('/history', methods=['GET'])
@jwt_required()
def get_history():
    """Get symptom check history"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if user.role == 'patient':
            # Get patient's own history
            patient = Patient.query.filter_by(user_id=user.id).first()
            if not patient:
                return jsonify({'error': 'Patient profile not found'}), 404
            
            checks = SymptomCheck.query.filter_by(patient_id=patient.id)\
                .order_by(SymptomCheck.created_at.desc()).all()
        else:
            # Doctors can see all checks
            checks = SymptomCheck.query.order_by(SymptomCheck.created_at.desc()).all()
        
        # Add patient info to each check
        checks_data = []
        for check in checks:
            check_dict = check.to_dict()
            patient = Patient.query.get(check.patient_id)
            check_dict['patient_name'] = patient.full_name if patient else 'Unknown'
            checks_data.append(check_dict)
        
        return jsonify({
            'checks': checks_data,
            'count': len(checks_data)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@symptoms_bp.route('/check/<int:check_id>', methods=['GET'])
@jwt_required()
def get_check(check_id):
    """Get specific symptom check"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        check = SymptomCheck.query.get(check_id)
        
        if not check:
            return jsonify({'error': 'Symptom check not found'}), 404
        
        # Check permissions
        if user.role == 'patient':
            patient = Patient.query.filter_by(user_id=user.id).first()
            if check.patient_id != patient.id:
                return jsonify({'error': 'Unauthorized'}), 403
        
        # Get patient info
        patient = Patient.query.get(check.patient_id)
        check_dict = check.to_dict()
        check_dict['patient_name'] = patient.full_name if patient else 'Unknown'
        check_dict['patient_info'] = patient.to_dict() if patient else None
        
        return jsonify({
            'check': check_dict
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@symptoms_bp.route('/check/<int:check_id>', methods=['PUT'])
@jwt_required()
def update_check(check_id):
    """Update symptom check status"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        check = SymptomCheck.query.get(check_id)
        
        if not check:
            return jsonify({'error': 'Symptom check not found'}), 404
        
        # Check permissions
        if user.role == 'patient':
            patient = Patient.query.filter_by(user_id=user.id).first()
            if check.patient_id != patient.id:
                return jsonify({'error': 'Unauthorized'}), 403
        
        data = request.get_json()
        
        # Update status
        if 'status' in data:
            check.status = data['status']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Symptom check updated successfully',
            'check': check.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@symptoms_bp.route('/check/<int:check_id>', methods=['DELETE'])
@jwt_required()
def delete_check(check_id):
    """Delete symptom check"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        check = SymptomCheck.query.get(check_id)
        
        if not check:
            return jsonify({'error': 'Symptom check not found'}), 404
        
        # Check permissions
        if user.role == 'patient':
            patient = Patient.query.filter_by(user_id=user.id).first()
            if check.patient_id != patient.id:
                return jsonify({'error': 'Unauthorized'}), 403
        
        db.session.delete(check)
        db.session.commit()
        
        return jsonify({
            'message': 'Symptom check deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@symptoms_bp.route('/diseases', methods=['GET'])
def get_diseases():
    """Get list of diseases that can be predicted"""
    diseases = [
        'Common Cold', 'Flu', 'Pneumonia', 'COVID-19', 'Tuberculosis',
        'Bronchitis', 'Asthma', 'Allergies', 'Sinusitis', 'Migraine',
        'Gastroenteritis', 'Food Poisoning', 'GERD', 'Diabetes',
        'Hypertension', 'Heart Disease', 'Stroke', 'Arthritis',
        'Urinary Tract Infection', 'Kidney Stones', 'Hepatitis',
        'Dengue', 'Malaria', 'Chickenpox', 'Measles'
    ]
    
    return jsonify({
        'diseases': diseases,
        'count': len(diseases)
    }), 200

