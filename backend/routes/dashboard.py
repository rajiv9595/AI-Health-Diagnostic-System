"""
Dashboard Routes for Statistics and Analytics
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.database import db, User, Patient, Doctor, XRayReport, SymptomCheck, Alert
from sqlalchemy import func, desc
from datetime import datetime, timedelta

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_stats():
    """Get dashboard statistics"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        print(f"Dashboard stats request from user_id: {user_id}, user: {user}")
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if user.role == 'doctor':
            # Doctor statistics
            total_patients = Patient.query.count()
            total_xray_reports = XRayReport.query.count()
            total_symptom_checks = SymptomCheck.query.count()
            urgent_cases = XRayReport.query.filter_by(status='urgent').count() + \
                          SymptomCheck.query.filter_by(urgency_level='severe').count()
            
            # Disease distribution from X-rays
            try:
                xray_diseases = db.session.query(
                    XRayReport.predicted_class,
                    func.count(XRayReport.id).label('count')
                ).group_by(XRayReport.predicted_class).all()
                
                disease_distribution = [
                    {'disease': disease, 'count': count}
                    for disease, count in xray_diseases
                ]
            except:
                disease_distribution = []
            
            # Recent activity (last 7 days)
            week_ago = datetime.utcnow() - timedelta(days=7)
            recent_xrays = XRayReport.query.filter(XRayReport.created_at >= week_ago).count()
            recent_symptoms = SymptomCheck.query.filter(SymptomCheck.created_at >= week_ago).count()
            
            # Urgency level distribution
            try:
                urgency_dist = db.session.query(
                    SymptomCheck.urgency_level,
                    func.count(SymptomCheck.id).label('count')
                ).group_by(SymptomCheck.urgency_level).all()
                
                urgency_distribution = [
                    {'level': level, 'count': count}
                    for level, count in urgency_dist
                ]
            except:
                urgency_distribution = []
            
            stats = {
                'overview': {
                    'total_patients': total_patients,
                    'total_xray_reports': total_xray_reports,
                    'total_symptom_checks': total_symptom_checks,
                    'urgent_cases': urgent_cases
                },
                'disease_distribution': disease_distribution,
                'urgency_distribution': urgency_distribution,
                'recent_activity': {
                    'xrays_last_7_days': recent_xrays,
                    'symptoms_last_7_days': recent_symptoms
                }
            }
            
        else:
            # Patient statistics
            patient = Patient.query.filter_by(user_id=user.id).first()
            if not patient:
                return jsonify({'error': 'Patient profile not found'}), 404
            
            total_xrays = XRayReport.query.filter_by(patient_id=patient.id).count()
            total_symptoms = SymptomCheck.query.filter_by(patient_id=patient.id).count()
            
            # Latest results
            latest_xray = XRayReport.query.filter_by(patient_id=patient.id)\
                .order_by(desc(XRayReport.created_at)).first()
            latest_symptom = SymptomCheck.query.filter_by(patient_id=patient.id)\
                .order_by(desc(SymptomCheck.created_at)).first()
            
            stats = {
                'overview': {
                    'total_xray_reports': total_xrays,
                    'total_symptom_checks': total_symptoms,
                    'latest_xray': latest_xray.to_dict() if latest_xray else None,
                    'latest_symptom': latest_symptom.to_dict() if latest_symptom else None
                }
            }
        
        return jsonify({
            'stats': stats,
            'role': user.role
        }), 200
        
    except Exception as e:
        print(f"Dashboard stats error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@dashboard_bp.route('/patients', methods=['GET'])
@jwt_required()
def get_patients():
    """Get all patients (doctor only)"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if not user or user.role != 'doctor':
            return jsonify({'error': 'Unauthorized - Doctor access required'}), 403
        
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        search = request.args.get('search', '', type=str)
        
        # Build query
        query = Patient.query
        
        if search:
            query = query.filter(Patient.full_name.ilike(f'%{search}%'))
        
        # Paginate
        pagination = query.order_by(desc(Patient.created_at)).paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        # Add additional info to each patient
        patients_data = []
        for patient in pagination.items:
            patient_dict = patient.to_dict()
            
            # Get latest X-ray
            latest_xray = XRayReport.query.filter_by(patient_id=patient.id)\
                .order_by(desc(XRayReport.created_at)).first()
            
            # Get latest symptom check
            latest_symptom = SymptomCheck.query.filter_by(patient_id=patient.id)\
                .order_by(desc(SymptomCheck.created_at)).first()
            
            # Count reports
            xray_count = XRayReport.query.filter_by(patient_id=patient.id).count()
            symptom_count = SymptomCheck.query.filter_by(patient_id=patient.id).count()
            
            patient_dict.update({
                'latest_xray': latest_xray.to_dict() if latest_xray else None,
                'latest_symptom': latest_symptom.to_dict() if latest_symptom else None,
                'xray_count': xray_count,
                'symptom_count': symptom_count
            })
            
            patients_data.append(patient_dict)
        
        return jsonify({
            'patients': patients_data,
            'pagination': {
                'page': pagination.page,
                'per_page': pagination.per_page,
                'total': pagination.total,
                'pages': pagination.pages
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@dashboard_bp.route('/patient/<int:patient_id>', methods=['GET'])
@jwt_required()
def get_patient_details(patient_id):
    """Get detailed patient information (doctor only)"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if not user or user.role != 'doctor':
            return jsonify({'error': 'Unauthorized - Doctor access required'}), 403
        
        patient = Patient.query.get(patient_id)
        
        if not patient:
            return jsonify({'error': 'Patient not found'}), 404
        
        # Get all reports
        xray_reports = XRayReport.query.filter_by(patient_id=patient_id)\
            .order_by(desc(XRayReport.created_at)).all()
        
        symptom_checks = SymptomCheck.query.filter_by(patient_id=patient_id)\
            .order_by(desc(SymptomCheck.created_at)).all()
        
        patient_dict = patient.to_dict()
        patient_dict.update({
            'xray_reports': [r.to_dict() for r in xray_reports],
            'symptom_checks': [s.to_dict() for s in symptom_checks]
        })
        
        return jsonify({
            'patient': patient_dict
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@dashboard_bp.route('/alerts', methods=['GET'])
@jwt_required()
def get_alerts():
    """Get alerts for doctors"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if user.role == 'doctor':
            # Get all unread alerts
            alerts = Alert.query.filter_by(is_read=False)\
                .order_by(desc(Alert.created_at)).all()
        else:
            # Patients see their own alerts
            patient = Patient.query.filter_by(user_id=user.id).first()
            if not patient:
                return jsonify({'error': 'Patient profile not found'}), 404
            
            alerts = Alert.query.filter_by(patient_id=patient.id)\
                .order_by(desc(Alert.created_at)).limit(10).all()
        
        # Add patient info to each alert
        alerts_data = []
        for alert in alerts:
            alert_dict = alert.to_dict()
            patient = Patient.query.get(alert.patient_id)
            alert_dict['patient_name'] = patient.full_name if patient else 'Unknown'
            alerts_data.append(alert_dict)
        
        return jsonify({
            'alerts': alerts_data,
            'count': len(alerts_data)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@dashboard_bp.route('/alert/<int:alert_id>/read', methods=['PUT'])
@jwt_required()
def mark_alert_read(alert_id):
    """Mark alert as read"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if not user or user.role != 'doctor':
            return jsonify({'error': 'Unauthorized - Doctor access required'}), 403
        
        alert = Alert.query.get(alert_id)
        
        if not alert:
            return jsonify({'error': 'Alert not found'}), 404
        
        alert.is_read = True
        db.session.commit()
        
        return jsonify({
            'message': 'Alert marked as read'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@dashboard_bp.route('/analytics/trends', methods=['GET'])
@jwt_required()
def get_trends():
    """Get disease trends over time (doctor only)"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if not user or user.role != 'doctor':
            return jsonify({'error': 'Unauthorized - Doctor access required'}), 403
        
        # Get time range from query params
        days = request.args.get('days', 30, type=int)
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # X-ray trends
        try:
            xray_trends = db.session.query(
                func.date(XRayReport.created_at).label('date'),
                XRayReport.predicted_class,
                func.count(XRayReport.id).label('count')
            ).filter(XRayReport.created_at >= start_date)\
             .group_by(func.date(XRayReport.created_at), XRayReport.predicted_class)\
             .all()
            
            xray_trends_data = [
                {
                    'date': date.isoformat() if hasattr(date, 'isoformat') else str(date),
                    'disease': disease,
                    'count': count
                }
                for date, disease, count in xray_trends
            ]
        except:
            xray_trends_data = []
        
        # Symptom trends
        try:
            symptom_trends = db.session.query(
                func.date(SymptomCheck.created_at).label('date'),
                SymptomCheck.predicted_disease,
                func.count(SymptomCheck.id).label('count')
            ).filter(SymptomCheck.created_at >= start_date)\
             .group_by(func.date(SymptomCheck.created_at), SymptomCheck.predicted_disease)\
             .all()
            
            symptom_trends_data = [
                {
                    'date': date.isoformat() if hasattr(date, 'isoformat') else str(date),
                    'disease': disease,
                    'count': count
                }
                for date, disease, count in symptom_trends
            ]
        except:
            symptom_trends_data = []
        
        return jsonify({
            'xray_trends': xray_trends_data,
            'symptom_trends': symptom_trends_data,
            'period_days': days
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

