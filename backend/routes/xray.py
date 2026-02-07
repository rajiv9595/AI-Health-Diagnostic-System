"""
X-ray Analysis Routes
"""
from flask import Blueprint, request, jsonify, current_app, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from models.database import db, User, Patient, XRayReport, Alert
from models.ml_models.covidnet_model import COVIDNetAnalyzer
import os
from datetime import datetime
from utils.gemini_service import verify_chest_xray

xray_bp = Blueprint('xray', __name__)

# Initialize X-ray analyzer (lazy loading)
xray_analyzer = None


def get_xray_analyzer():
    """Get or initialize COVID-Net analyzer"""
    global xray_analyzer
    if xray_analyzer is None:
        model_path = current_app.config['XRAY_MODEL_PATH']
        print(f"[INFO] Loading COVID-Net model...")
        print(f"[INFO] Model path: {model_path}")
        print(f"[INFO] Model exists: {os.path.exists(model_path)}")
        xray_analyzer = COVIDNetAnalyzer(model_path=model_path if os.path.exists(model_path) else None)
        print(f"[SUCCESS] COVID-Net analyzer initialized!")
    return xray_analyzer


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


@xray_bp.route('/upload', methods=['POST'])
@jwt_required()
def upload_xray():
    """Upload and analyze X-ray image"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get patient profile
        patient = Patient.query.filter_by(user_id=user.id).first()
        if not patient:
            return jsonify({'error': 'Patient profile not found'}), 404
        
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Allowed: png, jpg, jpeg'}), 400
        
        # Save file
        filename = secure_filename(f"{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}")
        upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'xrays', filename)
        file.save(upload_path)
        
        # Verify if it's actually an X-ray using Gemini
        is_xray, reason = verify_chest_xray(upload_path)
        if not is_xray:
            # Delete the invalid file
            if os.path.exists(upload_path):
                os.remove(upload_path)
            return jsonify({
                'error': 'Invalid image type',
                'message': f"This does not appear to be a chest X-ray. {reason}",
                'reason': reason
            }), 400
        
        # Analyze X-ray
        analyzer = get_xray_analyzer()
        
        # Get prediction
        print(f"[DEBUG] Analyzing X-ray: {upload_path}")
        print(f"[DEBUG] Analyzer model loaded: {analyzer.model is not None}")
        prediction = analyzer.predict(upload_path)
        print(f"[DEBUG] Prediction successful: {prediction}")
        
        # Try to generate Grad-CAM (non-critical, can fail gracefully)
        gradcam_path = None
        try:
            gradcam_filename = f"gradcam_{filename}"
            gradcam_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'gradcam', gradcam_filename)
            analyzer.generate_gradcam(upload_path, gradcam_path)
            print(f"[DEBUG] Grad-CAM generated successfully")
        except Exception as e:
            print(f"[WARNING] Grad-CAM generation failed (non-critical): {e}")
            gradcam_path = None  # Continue without Grad-CAM
        
        # Save report to database
        report = XRayReport(
            patient_id=patient.id,
            image_path=upload_path,
            gradcam_path=gradcam_path,
            predicted_class=prediction['predicted_class'],
            confidence=prediction['confidence'],
            notes=request.form.get('notes', '')
        )
        report.set_predictions(prediction['predictions'])
        
        # Add report first and flush to get ID before creating alert
        db.session.add(report)
        db.session.flush()

        # Set status based on prediction and create alert referencing report.id
        if prediction['is_abnormal'] and prediction['confidence'] > 0.7:
            report.status = 'urgent'
            alert = Alert(
                patient_id=patient.id,
                alert_type='xray',
                reference_id=report.id,
                message=f"Abnormal X-ray detected: {prediction['predicted_class']} ({prediction['confidence']*100:.1f}% confidence)",
                severity='high' if prediction['confidence'] > 0.8 else 'medium'
            )
            db.session.add(alert)
            print(f"🚨 ALERT: Patient {patient.full_name} - {alert.message}")

        db.session.commit()
        
        return jsonify({
            'message': 'X-ray analyzed successfully',
            'report': report.to_dict(),
            'patient_name': patient.full_name
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@xray_bp.route('/reports', methods=['GET'])
@jwt_required()
def get_reports():
    """Get X-ray reports for current user"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if user.role == 'patient':
            # Get patient's own reports
            patient = Patient.query.filter_by(user_id=user.id).first()
            if not patient:
                return jsonify({'error': 'Patient profile not found'}), 404
            
            reports = XRayReport.query.filter_by(patient_id=patient.id)\
                .order_by(XRayReport.created_at.desc()).all()
        else:
            # Doctors can see all reports
            reports = XRayReport.query.order_by(XRayReport.created_at.desc()).all()
        
        # Add patient info to each report
        reports_data = []
        for report in reports:
            report_dict = report.to_dict()
            patient = Patient.query.get(report.patient_id)
            report_dict['patient_name'] = patient.full_name if patient else 'Unknown'
            reports_data.append(report_dict)
        
        return jsonify({
            'reports': reports_data,
            'count': len(reports_data)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@xray_bp.route('/report/<int:report_id>', methods=['GET'])
@jwt_required()
def get_report(report_id):
    """Get specific X-ray report"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        report = XRayReport.query.get(report_id)
        
        if not report:
            return jsonify({'error': 'Report not found'}), 404
        
        # Check permissions
        if user.role == 'patient':
            patient = Patient.query.filter_by(user_id=user.id).first()
            if report.patient_id != patient.id:
                return jsonify({'error': 'Unauthorized'}), 403
        
        # Get patient info
        patient = Patient.query.get(report.patient_id)
        report_dict = report.to_dict()
        report_dict['patient_name'] = patient.full_name if patient else 'Unknown'
        report_dict['patient_info'] = patient.to_dict() if patient else None
        
        return jsonify({
            'report': report_dict
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@xray_bp.route('/image/<path:filename>', methods=['GET'])
# @jwt_required() - Disabled to allow <img> tags to load images
def get_image(filename):
    """Get X-ray or Grad-CAM image"""
    try:
        # Check if it's a gradcam image
        if filename.startswith('gradcam_'):
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'gradcam', filename)
        else:
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'xrays', filename)
        
        if not os.path.exists(file_path):
            return jsonify({'error': 'Image not found'}), 404
        
        return send_file(file_path, mimetype='image/jpeg')
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@xray_bp.route('/report/<int:report_id>', methods=['PUT'])
@jwt_required()
def update_report(report_id):
    """Update X-ray report (doctor only)"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if not user or user.role != 'doctor':
            return jsonify({'error': 'Unauthorized - Doctor access required'}), 403
        
        report = XRayReport.query.get(report_id)
        
        if not report:
            return jsonify({'error': 'Report not found'}), 404
        
        data = request.get_json()
        
        # Update fields
        if 'notes' in data:
            report.notes = data['notes']
        if 'status' in data:
            report.status = data['status']
        
        doctor = User.query.get(user_id).doctor_profile
        if doctor:
            report.reviewed_by = doctor.id
        
        db.session.commit()
        
        return jsonify({
            'message': 'Report updated successfully',
            'report': report.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@xray_bp.route('/report/<int:report_id>', methods=['DELETE'])
@jwt_required()
def delete_report(report_id):
    """Delete X-ray report"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        report = XRayReport.query.get(report_id)
        
        if not report:
            return jsonify({'error': 'Report not found'}), 404
        
        # Check permissions
        if user.role == 'patient':
            patient = Patient.query.filter_by(user_id=user.id).first()
            if report.patient_id != patient.id:
                return jsonify({'error': 'Unauthorized'}), 403
        
        # Delete files
        if os.path.exists(report.image_path):
            os.remove(report.image_path)
        if report.gradcam_path and os.path.exists(report.gradcam_path):
            os.remove(report.gradcam_path)
        
        db.session.delete(report)
        db.session.commit()
        
        return jsonify({
            'message': 'Report deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

