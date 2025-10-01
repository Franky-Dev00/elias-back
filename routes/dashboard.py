from flask import Blueprint, jsonify
from models import db, Patient, ClinicalRecord, User
from flask_jwt_extended import jwt_required
from sqlalchemy import func, desc
from datetime import datetime, timedelta

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@dashboard_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_stats():
    try:
        # Estadísticas generales
        total_patients = Patient.query.count()
        total_clinical_records = ClinicalRecord.query.count()
        total_users = User.query.count()
        
        # Estadísticas de hoy
        today = datetime.now().date()
        new_patients_today = Patient.query.filter(
            func.date(Patient.created_at) == today
        ).count()
        
        new_records_today = ClinicalRecord.query.filter(
            func.date(ClinicalRecord.created_at) == today
        ).count()
        
        # Pacientes recientes (últimos 5)
        recent_patients = Patient.query.order_by(
            desc(Patient.created_at)
        ).limit(5).all()
        
        # Fichas clínicas recientes (últimas 5)
        recent_records = ClinicalRecord.query.order_by(
            desc(ClinicalRecord.created_at)
        ).limit(5).all()
        
        # Distribución por género
        gender_stats = db.session.query(
            Patient.gender,
            func.count(Patient.id).label('count')
        ).group_by(Patient.gender).all()
        
        gender_distribution = {}
        for gender, count in gender_stats:
            gender_key = 'Masculino' if gender == 'male' else 'Femenino' if gender == 'female' else 'Otro'
            gender_distribution[gender_key] = count
        
        # Distribución por rol de usuarios
        role_stats = db.session.query(
            User.role,
            func.count(User.id).label('count')
        ).group_by(User.role).all()
        
        users_by_role = {}
        for role, count in role_stats:
            role_key = {
                'administrador': 'Administrador',
                'medico': 'Médico',
                'tecnico': 'Técnico',
                'administrativo': 'Administrativo'
            }.get(role, role.title())
            users_by_role[role_key] = count
        
        return jsonify({
            'general_stats': {
                'total_patients': total_patients,
                'total_clinical_records': total_clinical_records,
                'total_users': total_users,
                'total_tasks': 0  # Placeholder para tareas
            },
            'today_stats': {
                'new_patients': new_patients_today,
                'new_records': new_records_today
            },
            'recent_activity': {
                'recent_patients': [
                    {
                        'id': patient.id,
                        'full_name': patient.full_name,
                        'created_at': patient.created_at.isoformat()
                    } for patient in recent_patients
                ],
                'recent_records': [
                    {
                        'id': record.id,
                        'patient_name': record.patient.full_name if record.patient else 'Paciente no encontrado',
                        'doctor_name': record.doctor_name,  # Usar campo inmutable
                        'visit_date': record.visit_date.isoformat()
                    } for record in recent_records
                ]
            },
            'gender_distribution': gender_distribution,
            'users_by_role': users_by_role,
            'tasks_status': {
                'completion_rate': 0  # Placeholder
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500