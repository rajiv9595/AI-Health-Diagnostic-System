
import os
import sys
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import sessionmaker
import config

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models.database import db, User, Patient, Doctor, XRayReport, SymptomCheck, Alert

def migrate_data(target_db_url):
    """
    Migrate data from local SQLite to Supabase (PostgreSQL)
    """
    print(f"Target DB: {target_db_url.split('@')[1] if '@' in target_db_url else '...'}")
    
    # 1. Initialize App with Source DB (Local)
    app = create_app('development')
    
    # 2. Create Target Engine
    target_engine = create_engine(target_db_url)
    TargetSession = sessionmaker(bind=target_engine)
    target_session = TargetSession()
    
    with app.app_context():
        print("Connected to Source DB (SQLite)...")
        
        # Ensure Target Tables Exist
        print("Creating tables in Target DB...")
        db.metadata.create_all(target_engine)
        
        # --- Migrate Users ---
        print("Migrating Users...")
        users = User.query.all()
        for u in users:
            # Check if exists
            exists = target_session.execute(
                Table('user', MetaData(), autoload_with=target_engine).select().where(Table('user', MetaData(), autoload_with=target_engine).c.email == u.email)
            ).first()
            
            if not exists:
                new_user = User(
                    email=u.email,
                    password_hash=u.password_hash,
                    role=u.role,
                    created_at=u.created_at
                )
                # Force ID to match to keep relationships intact
                new_user.id = u.id 
                target_session.merge(new_user)
        target_session.commit()
        
        # --- Migrate Doctors ---
        print("Migrating Doctors...")
        doctors = Doctor.query.all()
        for d in doctors:
            new_doc = Doctor(
                id=d.id,
                user_id=d.user_id,
                full_name=d.full_name,
                specialization=d.specialization,
                license_number=d.license_number,
                phone=d.phone,
                hospital=d.hospital,
                created_at=d.created_at
            )
            target_session.merge(new_doc)
        target_session.commit()

        # --- Migrate Patients ---
        print("Migrating Patients...")
        patients = Patient.query.all()
        for p in patients:
            new_pat = Patient(
                id=p.id,
                user_id=p.user_id,
                full_name=p.full_name,
                dob=p.dob,
                gender=p.gender,
                phone=p.phone,
                address=p.address,
                medical_history=p.medical_history,
                created_at=p.created_at
            )
            target_session.merge(new_pat)
        target_session.commit()

        # --- Migrate XRayReports ---
        print("Migrating X-Ray Reports...")
        reports = XRayReport.query.all()
        for r in reports:
            new_report = XRayReport(
                id=r.id,
                patient_id=r.patient_id,
                doctor_id=r.doctor_id,
                image_path=r.image_path,
                prediction=r.prediction,
                confidence=r.confidence,
                details=r.details,
                gradcam_path=r.gradcam_path,
                status=r.status,
                predicted_class=r.predicted_class, # Ensure this field exists in model
                created_at=r.created_at
            )
            target_session.merge(new_report)
        target_session.commit()
        
        # --- Migrate SymptomChecks ---
        print("Migrating Symptom Checks...")
        checks = SymptomCheck.query.all()
        for c in checks:
            new_check = SymptomCheck(
                id=c.id,
                patient_id=c.patient_id,
                symptoms=c.symptoms,
                predicted_disease=c.predicted_disease,
                confidence=c.confidence,
                recommendations=c.recommendations,
                urgency_level=c.urgency_level,
                created_at=c.created_at
            )
            target_session.merge(new_check)
        target_session.commit()
        
        print("✅ Migration Complete!")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python migrate_to_supabase.py <SUPABASE_CONNECTION_STRING>")
        print("Example: python migrate_to_supabase.py postgresql://user:pass@host:port/db")
        sys.exit(1)
        
    target_url = sys.argv[1]
    # SQLAlchemy requires 'postgresql://' not 'postgres://' which Supabase sometimes gives
    if target_url.startswith('postgres://'):
        target_url = target_url.replace('postgres://', 'postgresql://', 1)
        
    try:
        migrate_data(target_url)
    except Exception as e:
        print(f"❌ Migration Failed: {e}")
        import traceback
        traceback.print_exc()
