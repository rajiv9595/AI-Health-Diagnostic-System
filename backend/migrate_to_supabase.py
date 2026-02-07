import sys
import os
from flask import Flask
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, make_transient
# Skip 'from app import create_app' to avoid TensorFlow/OpenCV DLL issues
from models.database import db, User, Patient, Doctor, XRayReport, SymptomCheck, Alert
from config import config

def create_minimal_app(config_name='development'):
    app = Flask(__name__)
    # Load config but FORCE SQLite for source extraction
    # This prevents accidental connection to Supabase if .env is loaded
    app.config.from_object(config[config_name])
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'health_diagnostic.db')
    db.init_app(app)
    return app

def migrate_to_supabase():
    # 1. Setup - Get Supabase URL
    print("\n📦 Database Migration Tool (Local -> Supabase)")
    print("WARNING: This will overwrite data in the target Supabase database if tables exist.")
    supabase_url = input("Enter your Supabase Connection String (postgresql://...): ").strip()
    
    if not supabase_url.startswith("postgresql://") and not supabase_url.startswith("postgres://"):
        print("Invalid URL format. Must start with postgresql://")
        return

    # Fix for sqlalchemy expecting postgresql:// not postgres://
    if supabase_url.startswith("postgres://"):
        supabase_url = supabase_url.replace("postgres://", "postgresql://", 1)

    # 2. Extract Data from Local SQLite
    print("\nExtracting data from local database...")
    
    # Force SQLite for source (ignore .env if set)
    if 'DATABASE_URL' in os.environ:
        del os.environ['DATABASE_URL']
        
    local_app = create_minimal_app('development')
    
    data_map = {}
    with local_app.app_context():
        # Order matters for foreign keys!
        # Users first, then Profiles (Patient/Doctor), then Reports/Alerts
        try:
            users = User.query.all()
            patients = Patient.query.all()
            doctors = Doctor.query.all()
            reports = XRayReport.query.all()
            checks = SymptomCheck.query.all()
            alerts = Alert.query.all()
            
            # Detach objects from session so we can attach to new one
            for collection in [users, patients, doctors, reports, checks, alerts]:
                for obj in collection:
                    db.session.expunge(obj)
                    make_transient(obj)
            
            data_map = {
                'users': users,
                'patients': patients,
                'doctors': doctors,
                'reports': reports,
                'checks': checks,
                'alerts': alerts
            }
            print(f"Loaded: {len(users)} users, {len(patients)} patients, {len(doctors)} doctors...")
            
        except Exception as e:
            print(f"Error reading local DB: {e}")
            return

    # 3. Connect to Supabase and Insert
    print(f"\nConnecting to Supabase...")
    target_engine = create_engine(supabase_url)
    Session = sessionmaker(bind=target_engine)
    session = Session()

    try:
        # Create Tables
        print("Creating tables on Supabase...")
        # We need to bind the metadata to the new engine to create tables
        db.metadata.create_all(target_engine)
        
        # Insert Data
        print("Migrating data...")
        
        # Users
        for u in data_map['users']:
            session.merge(u) # Merge handles explicit IDs better
        session.flush()
        
        # Profiles
        for p in data_map['patients']: session.merge(p)
        for d in data_map['doctors']: session.merge(d)
        session.flush()
        
        # Data
        for r in data_map['reports']: session.merge(r)
        for c in data_map['checks']: session.merge(c)
        for a in data_map['alerts']: session.merge(a)
        
        session.commit()
        print("✅ Data migration successful!")
        
        # 4. Update Sequences (Essential for Postgres)
        print("Updating ID sequences...")
        tables = ['users', 'patients', 'doctors', 'xray_reports', 'symptom_checks', 'alerts']
        # Note: Table names might differ slightly in DB (e.g. user vs users). 
        # Checking models.database.py for __tablename__ is better, or assuming defaults.
        # SQLAlchemy default is snake_case of class name usually, but let's check.
        # Check actual table names:
        with target_engine.connect() as conn:
            for table in tables:
                try:
                    # Postgres sequence naming convention: table_id_seq
                    seq_name = f"{table}_id_seq"
                    # Reset sequence to max id
                    sql = text(f"SELECT setval('{seq_name}', (SELECT MAX(id) FROM {table}));")
                    conn.execute(sql)
                    print(f"  Fixed sequence for {table}")
                except Exception as ex:
                    print(f"  Skipping sequence update for {table} (might not exist or different name): {ex}")
            conn.commit()
            
    except Exception as e:
        session.rollback()
        print(f"❌ Migration failed: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    migrate_to_supabase()
