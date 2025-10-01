from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from models import Appointment, Patient, User, db
from flask_jwt_extended import jwt_required, get_jwt_identity
from utils.permissions import role_required
from sqlalchemy import desc, and_, or_

appointments_bp = Blueprint('appointments', __name__, url_prefix='/appointments')

@appointments_bp.route('/', methods=['GET'])
@jwt_required()
def get_appointments():
    """Obtener todas las citas con filtros opcionales"""
    try:
        query = Appointment.query
        
        # Filtros opcionales
        status = request.args.get('status')
        patient_id = request.args.get('patient_id')
        doctor_id = request.args.get('doctor_id')
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        
        if status:
            query = query.filter_by(status=status)
        if patient_id:
            query = query.filter_by(patient_id=int(patient_id))
        if doctor_id:
            query = query.filter_by(doctor_id_snapshot=int(doctor_id))
        if date_from:
            query = query.filter(Appointment.appointment_date >= datetime.fromisoformat(date_from))
        if date_to:
            query = query.filter(Appointment.appointment_date <= datetime.fromisoformat(date_to))
        
        appointments = query.order_by(Appointment.appointment_date).all()
        return jsonify([appointment.to_dict() for appointment in appointments])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@appointments_bp.route('/<int:appointment_id>', methods=['GET'])
@jwt_required()
def get_appointment(appointment_id):
    """Obtener una cita específica"""
    try:
        appointment = Appointment.query.get_or_404(appointment_id)
        return jsonify(appointment.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@appointments_bp.route('/patient/<int:patient_id>', methods=['GET'])
@jwt_required()
def get_patient_appointments(patient_id):
    """Obtener citas de un paciente específico"""
    try:
        patient = Patient.query.get_or_404(patient_id)
        appointments = Appointment.query.filter_by(
            patient_id=patient_id
        ).order_by(desc(Appointment.appointment_date)).all()
        
        return jsonify([appointment.to_dict() for appointment in appointments])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@appointments_bp.route('/today', methods=['GET'])
@jwt_required()
def get_today_appointments():
    """Obtener citas del día actual"""
    try:
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)
        
        appointments = Appointment.query.filter(
            and_(
                Appointment.appointment_date >= today_start,
                Appointment.appointment_date < today_end
            )
        ).order_by(Appointment.appointment_date).all()
        
        return jsonify([appointment.to_dict() for appointment in appointments])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@appointments_bp.route('/upcoming', methods=['GET'])
@jwt_required()
def get_upcoming_appointments():
    """Obtener próximas citas (próximos 7 días)"""
    try:
        now = datetime.now()
        week_later = now + timedelta(days=7)
        
        appointments = Appointment.query.filter(
            and_(
                Appointment.appointment_date >= now,
                Appointment.appointment_date <= week_later,
                Appointment.status.in_(['pendiente', 'confirmada'])
            )
        ).order_by(Appointment.appointment_date).limit(10).all()
        
        return jsonify([appointment.to_dict() for appointment in appointments])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@appointments_bp.route('/', methods=['POST'])
@jwt_required()
@role_required('administrador', 'medico', 'tecnico', 'administrativo')
def create_appointment():
    """Crear nueva cita"""
    try:
        data = request.json
        current_user_id = int(get_jwt_identity())
        
        # Validaciones básicas
        if not data.get('patient_id'):
            return jsonify({'error': 'El ID del paciente es obligatorio'}), 400
        if not data.get('doctor_id'):
            return jsonify({'error': 'El ID del médico es obligatorio'}), 400
        if not data.get('appointment_date'):
            return jsonify({'error': 'La fecha de la cita es obligatoria'}), 400
        if not data.get('appointment_type'):
            return jsonify({'error': 'El tipo de cita es obligatorio'}), 400
        if not data.get('reason'):
            return jsonify({'error': 'El motivo de la cita es obligatorio'}), 400
        
        # Verificar que el paciente existe
        patient = Patient.query.get(data['patient_id'])
        if not patient:
            return jsonify({'error': 'El paciente especificado no existe'}), 400
        
        # Verificar que el médico existe
        doctor = User.query.get(data['doctor_id'])
        if not doctor:
            return jsonify({'error': 'El médico especificado no existe'}), 400
        if doctor.role not in ['medico', 'administrador']:
            return jsonify({'error': 'El usuario seleccionado no es un médico'}), 400
        
        # Obtener usuario que crea la cita
        creator = User.query.get(current_user_id)
        if not creator:
            return jsonify({'error': 'Usuario creador no encontrado'}), 404
        
        # Parsear fecha
        appointment_datetime = datetime.fromisoformat(data['appointment_date'])
        
        # Verificar que la cita no sea en el pasado
        if appointment_datetime < datetime.now():
            return jsonify({'error': 'No se pueden crear citas en fechas pasadas'}), 400
        
        # Verificar conflictos de horario para el médico
        duration = data.get('duration_minutes', 30)
        appointment_end = appointment_datetime + timedelta(minutes=duration)
        
        conflicting_appointments = Appointment.query.filter(
            and_(
                Appointment.doctor_id_snapshot == doctor.id,
                Appointment.status.in_(['pendiente', 'confirmada']),
                or_(
                    # La nueva cita comienza durante una cita existente
                    and_(
                        Appointment.appointment_date <= appointment_datetime,
                        Appointment.appointment_date + timedelta(minutes=Appointment.duration_minutes) > appointment_datetime
                    ),
                    # La nueva cita termina durante una cita existente
                    and_(
                        Appointment.appointment_date < appointment_end,
                        Appointment.appointment_date + timedelta(minutes=Appointment.duration_minutes) >= appointment_end
                    ),
                    # La nueva cita envuelve completamente una cita existente
                    and_(
                        Appointment.appointment_date >= appointment_datetime,
                        Appointment.appointment_date + timedelta(minutes=Appointment.duration_minutes) <= appointment_end
                    )
                )
            )
        ).first()
        
        if conflicting_appointments:
            return jsonify({
                'error': f'El médico ya tiene una cita programada a las {conflicting_appointments.appointment_date.strftime("%H:%M")}'
            }), 409
        
        # Preparar datos de la cita
        appointment_data = {
            'appointment_date': appointment_datetime,
            'duration_minutes': duration,
            'appointment_type': data['appointment_type'],
            'reason': data['reason'],
            'status': data.get('status', 'pendiente'),
            'observations': data.get('observations')
        }
        
        # Crear cita con información inmutable
        appointment = Appointment.create_with_users_info(
            patient_id=data['patient_id'],
            doctor_user=doctor,
            creator_user=creator,
            appointment_data=appointment_data
        )
        
        db.session.add(appointment)
        db.session.commit()
        
        return jsonify({
            'message': 'Cita creada exitosamente',
            'appointment': appointment.to_dict()
        }), 201
        
    except ValueError as ve:
        db.session.rollback()
        return jsonify({'error': f'Error en formato de datos: {str(ve)}'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@appointments_bp.route('/<int:appointment_id>', methods=['PUT'])
@jwt_required()
@role_required('administrador', 'medico', 'tecnico', 'administrativo')
def update_appointment(appointment_id):
    """Actualizar cita existente"""
    try:
        appointment = Appointment.query.get_or_404(appointment_id)
        data = request.json
        
        # No permitir actualizar citas completadas o muy antiguas
        if appointment.status == 'completada':
            return jsonify({'error': 'No se pueden modificar citas completadas'}), 400
        
        # Actualizar campos permitidos
        if 'appointment_date' in data:
            new_date = datetime.fromisoformat(data['appointment_date'])
            if new_date < datetime.now():
                return jsonify({'error': 'No se puede reprogramar a una fecha pasada'}), 400
            appointment.appointment_date = new_date
        
        if 'duration_minutes' in data:
            appointment.duration_minutes = int(data['duration_minutes'])
        if 'appointment_type' in data:
            appointment.appointment_type = data['appointment_type']
        if 'reason' in data:
            appointment.reason = data['reason']
        if 'status' in data:
            appointment.status = data['status']
        if 'observations' in data:
            appointment.observations = data['observations']
        if 'cancellation_reason' in data:
            appointment.cancellation_reason = data['cancellation_reason']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Cita actualizada exitosamente',
            'appointment': appointment.to_dict()
        })
        
    except ValueError as ve:
        db.session.rollback()
        return jsonify({'error': f'Error en formato de datos: {str(ve)}'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@appointments_bp.route('/<int:appointment_id>', methods=['DELETE'])
@jwt_required()
@role_required('administrador', 'administrativo')
def delete_appointment(appointment_id):
    """Eliminar cita - Solo administrador y administrativo"""
    try:
        appointment = Appointment.query.get_or_404(appointment_id)
        db.session.delete(appointment)
        db.session.commit()
        return jsonify({'message': 'Cita eliminada exitosamente'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@appointments_bp.route('/<int:appointment_id>/cancel', methods=['POST'])
@jwt_required()
@role_required('administrador', 'medico', 'tecnico', 'administrativo')
def cancel_appointment(appointment_id):
    """Cancelar una cita"""
    try:
        appointment = Appointment.query.get_or_404(appointment_id)
        data = request.json
        
        if appointment.status in ['completada', 'cancelada']:
            return jsonify({'error': f'La cita ya está {appointment.status}'}), 400
        
        appointment.status = 'cancelada'
        appointment.cancellation_reason = data.get('cancellation_reason', 'Sin especificar')
        
        db.session.commit()
        
        return jsonify({
            'message': 'Cita cancelada exitosamente',
            'appointment': appointment.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500