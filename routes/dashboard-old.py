from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from models import Patient, ClinicalRecord, User, Task, db
from datetime import datetime, timedelta
from sqlalchemy import func

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@dashboard_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_dashboard_stats():
    try:
        # Estadísticas generales
        total_patients = Patient.query.count()
        total_clinical_records = ClinicalRecord.query.count()
        total_users = User.query.count()
        total_tasks = Task.query.count()
        
        # Estadísticas de hoy
        today = datetime.utcnow().date()
        today_start = datetime(today.year, today.month, today.day)
        patients_today = Patient.query.filter(Patient.created_at >= today_start).count()
        records_today = ClinicalRecord.query.filter(ClinicalRecord.visit_date >= today_start).count()
        
        # Estadísticas de la semana
        week_ago = datetime.utcnow() - timedelta(days=7)
        patients_this_week = Patient.query.filter(Patient.created_at >= week_ago).count()
        records_this_week = ClinicalRecord.query.filter(ClinicalRecord.visit_date >= week_ago).count()
        
        # Distribución por género
        gender_stats = db.session.query(
            Patient.gender, 
            func.count(Patient.id)
        ).group_by(Patient.gender).all()
        
        # Tareas pendientes vs completadas
        tasks_done = Task.query.filter_by(done=True).count()
        tasks_pending = Task.query.filter_by(done=False).count()
        
        # Usuarios por rol
        role_stats = db.session.query(
            User.role, 
            func.count(User.id)
        ).group_by(User.role).all()
        
        # Últimos 5 pacientes registrados
        recent_patients = Patient.query.order_by(Patient.created_at.desc()).limit(5).all()
        
        # Últimas 5 fichas clínicas - CON MANEJO DE ERRORES
        recent_records = ClinicalRecord.query.order_by(ClinicalRecord.visit_date.desc()).limit(5).all()
        
        # Estadísticas de fichas clínicas por médico
        records_by_doctor = db.session.query(
            User.full_name,
            func.count(ClinicalRecord.id)
        ).join(ClinicalRecord, ClinicalRecord.doctor_id == User.id).group_by(User.id, User.full_name).all()
        
        return jsonify({
            'general_stats': {
                'total_patients': total_patients,
                'total_clinical_records': total_clinical_records,
                'total_users': total_users,
                'total_tasks': total_tasks
            },
            'today_stats': {
                'new_patients': patients_today,
                'new_records': records_today
            },
            'weekly_stats': {
                'new_patients_week': patients_this_week,
                'new_records_week': records_this_week
            },
            'gender_distribution': {
                gender: count for gender, count in gender_stats
            },
            'tasks_status': {
                'completed': tasks_done,
                'pending': tasks_pending,
                'completion_rate': round((tasks_done / total_tasks * 100), 2) if total_tasks > 0 else 0
            },
            'users_by_role': {
                role: count for role, count in role_stats
            },
            'recent_activity': {
                'recent_patients': [{
                    'id': p.id,
                    'rut': p.rut,
                    'full_name': p.full_name,
                    'created_at': p.created_at.isoformat()
                } for p in recent_patients],
                'recent_records': [{
                    'id': r.id,
                    'patient_name': r.patient.full_name if r.patient else 'Paciente no encontrado',
                    'doctor_name': r.doctor.full_name if r.doctor else 'Médico no encontrado',
                    'visit_date': r.visit_date.isoformat(),
                    'diagnosis': (r.diagnosis[:50] + '...') if r.diagnosis and len(r.diagnosis) > 50 else r.diagnosis
                } for r in recent_records]
            },
            'records_by_doctor': {
                doctor_name: count for doctor_name, count in records_by_doctor
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dashboard_bp.route('/patient-stats/<int:patient_id>', methods=['GET'])
@jwt_required()
def get_patient_stats(patient_id):
    try:
        patient = Patient.query.get_or_404(patient_id)
        
        # Estadísticas del paciente
        total_visits = ClinicalRecord.query.filter_by(patient_id=patient_id).count()
        
        # Última visita - CON MANEJO DE ERRORES
        last_visit = ClinicalRecord.query.filter_by(patient_id=patient_id).order_by(ClinicalRecord.visit_date.desc()).first()
        
        # Visitas por mes (últimos 6 meses)
        six_months_ago = datetime.utcnow() - timedelta(days=180)
        visits_by_month = db.session.query(
            func.date_trunc('month', ClinicalRecord.visit_date),
            func.count(ClinicalRecord.id)
        ).filter(
            ClinicalRecord.patient_id == patient_id,
            ClinicalRecord.visit_date >= six_months_ago
        ).group_by(func.date_trunc('month', ClinicalRecord.visit_date)).all()
        
        # Diagnósticos más comunes
        common_diagnoses = db.session.query(
            ClinicalRecord.diagnosis,
            func.count(ClinicalRecord.id)
        ).filter(
            ClinicalRecord.patient_id == patient_id,
            ClinicalRecord.diagnosis.isnot(None)
        ).group_by(ClinicalRecord.diagnosis).order_by(func.count(ClinicalRecord.id).desc()).limit(5).all()
        
        return jsonify({
            'patient_info': {
                'id': patient.id,
                'rut': patient.rut,
                'full_name': patient.full_name,
                'age': calculate_age(patient.birth_date),
                'blood_type': patient.blood_type,
                'allergies': patient.allergies,
                'chronic_diseases': patient.chronic_diseases
            },
            'visit_stats': {
                'total_visits': total_visits,
                'last_visit': last_visit.visit_date.isoformat() if last_visit else None,
                'last_doctor': last_visit.doctor.full_name if last_visit and last_visit.doctor else None,
                'visits_by_month': [{
                    'month': month.strftime('%Y-%m'),
                    'count': count
                } for month, count in visits_by_month]
            },
            'medical_info': {
                'common_diagnoses': [{
                    'diagnosis': diagnosis,
                    'count': count
                } for diagnosis, count in common_diagnoses]
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def calculate_age(birth_date):
    """Calcular edad basada en la fecha de nacimiento"""
    if not birth_date:
        return None
    today = datetime.utcnow().date()
    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

@dashboard_bp.route('/doctor-stats/<int:doctor_id>', methods=['GET'])
@jwt_required()
def get_doctor_stats(doctor_id):
    try:
        doctor = User.query.get_or_404(doctor_id)
        if doctor.role not in ['medico', 'admin']:
            return jsonify({'error': 'El usuario no es un médico'}), 400
        
        # Estadísticas del médico
        total_records = ClinicalRecord.query.filter_by(doctor_id=doctor_id).count()
        
        # Registros de hoy
        today = datetime.utcnow().date()
        today_start = datetime(today.year, today.month, today.day)
        records_today = ClinicalRecord.query.filter(
            ClinicalRecord.doctor_id == doctor_id,
            ClinicalRecord.visit_date >= today_start
        ).count()
        
        # Registros de la semana
        week_ago = datetime.utcnow() - timedelta(days=7)
        records_week = ClinicalRecord.query.filter(
            ClinicalRecord.doctor_id == doctor_id,
            ClinicalRecord.visit_date >= week_ago
        ).count()
        
        # Pacientes únicos atendidos
        unique_patients = db.session.query(func.count(func.distinct(ClinicalRecord.patient_id))).filter_by(doctor_id=doctor_id).scalar()
        
        # Últimos registros - CON MANEJO DE ERRORES
        recent_records = ClinicalRecord.query.filter_by(doctor_id=doctor_id).order_by(ClinicalRecord.visit_date.desc()).limit(10).all()
        
        return jsonify({
            'doctor_info': {
                'id': doctor.id,
                'full_name': doctor.full_name,
                'role': doctor.role
            },
            'stats': {
                'total_records': total_records,
                'records_today': records_today,
                'records_this_week': records_week,
                'unique_patients': unique_patients
            },
            'recent_activity': [{
                'id': record.id,
                'patient_name': record.patient.full_name if record.patient else 'Paciente no encontrado',
                'visit_date': record.visit_date.isoformat(),
                'diagnosis': (record.diagnosis[:30] + '...') if record.diagnosis and len(record.diagnosis) > 30 else record.diagnosis
            } for record in recent_records]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
