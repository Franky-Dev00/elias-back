from flask import Blueprint, request, jsonify
from datetime import datetime
from models import ClinicalRecord, Patient, User, db
from flask_jwt_extended import jwt_required, get_jwt_identity
from utils.permissions import role_required
from sqlalchemy import desc

clinical_records_bp = Blueprint('clinical_records', __name__, url_prefix='/clinical-records')

@clinical_records_bp.route('/', methods=['GET'])
@jwt_required()
def get_clinical_records():
    try:
        records = ClinicalRecord.query.order_by(desc(ClinicalRecord.created_at)).all()
        return jsonify([record.to_dict() for record in records])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@clinical_records_bp.route('/<int:record_id>', methods=['GET'])
@jwt_required()
def get_clinical_record(record_id):
    try:
        record = ClinicalRecord.query.get_or_404(record_id)
        return jsonify(record.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@clinical_records_bp.route('/', methods=['POST'])
@jwt_required()
@role_required('administrador', 'medico')  # CORREGIDO: usar 'administrador' no 'admin'
def create_clinical_record():
    try:
        data = request.json
        current_user_id = int(get_jwt_identity())  # CORREGIDO: convertir a int
        
        # Validaciones básicas mejoradas
        if not data.get('patient_id'):
            return jsonify({'error': 'El ID del paciente es obligatorio'}), 400
        if not data.get('visit_date'):
            return jsonify({'error': 'La fecha de consulta es obligatoria'}), 400
        if not data.get('reason_visit'):  # NUEVO: validar motivo de consulta
            return jsonify({'error': 'El motivo de consulta es obligatorio'}), 400
        if not data.get('diagnosis'):
            return jsonify({'error': 'El diagnóstico es obligatorio'}), 400
        
        # Verificar que el paciente existe
        patient = Patient.query.get(data['patient_id'])
        if not patient:
            return jsonify({'error': 'El paciente especificado no existe'}), 400
        
        # Verificar que el usuario (médico) existe
        doctor = User.query.get(current_user_id)
        if not doctor:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        # Calcular IMC si se proporcionan peso y altura
        bmi = None
        if data.get('weight') and data.get('height'):
            try:
                weight = float(data['weight'])
                height = float(data['height']) / 100  # convertir cm a metros
                bmi = round(weight / (height ** 2), 1)
            except (ValueError, ZeroDivisionError):
                bmi = None
        
        record = ClinicalRecord(
            patient_id=data['patient_id'],
            doctor_id=current_user_id,
            visit_date=datetime.fromisoformat(data['visit_date']) if data.get('visit_date') else datetime.utcnow(),
            symptoms=data.get('symptoms'),
            diagnosis=data.get('diagnosis'),
            treatment=data.get('treatment'),
            prescriptions=data.get('prescriptions'),
            notes=data.get('observations'),  # CORREGIDO: mapear 'observations' a 'notes'
            blood_pressure=data.get('blood_pressure'),
            heart_rate=int(data['heart_rate']) if data.get('heart_rate') and data['heart_rate'] != '' else None,
            temperature=float(data['temperature']) if data.get('temperature') and data['temperature'] != '' else None,
            weight=float(data['weight']) if data.get('weight') and data['weight'] != '' else None,
            height=float(data['height']) if data.get('height') and data['height'] != '' else None,
            bmi=bmi,  # CORREGIDO: usar el IMC calculado
            next_appointment=datetime.fromisoformat(data['next_appointment']) if data.get('next_appointment') and data['next_appointment'] != '' else None
        )
        
        db.session.add(record)
        db.session.commit()
        
        return jsonify({
            'message': 'Ficha clínica creada exitosamente',
            'clinical_record': record.to_dict()
        }), 201
        
    except ValueError as ve:
        db.session.rollback()
        return jsonify({'error': f'Error en formato de datos: {str(ve)}'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@clinical_records_bp.route('/patient/<int:patient_id>', methods=['GET'])
@jwt_required()
def get_patient_records(patient_id):
    try:
        # Verificar que el paciente existe
        patient = Patient.query.get_or_404(patient_id)
        
        records = ClinicalRecord.query.filter_by(
            patient_id=patient_id
        ).order_by(desc(ClinicalRecord.created_at)).all()
        
        return jsonify([record.to_dict() for record in records])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@clinical_records_bp.route('/<int:record_id>', methods=['PUT'])
@jwt_required()
@role_required('administrador', 'medico')  # CORREGIDO: usar 'administrador' no 'admin'
def update_clinical_record(record_id):
    try:
        record = ClinicalRecord.query.get_or_404(record_id)
        data = request.json
        current_user_id = int(get_jwt_identity())  # CORREGIDO: convertir a int
        user = User.query.get(current_user_id)
        
        # Solo el médico que creó la ficha o un administrador pueden editarla
        if user.role != 'administrador' and record.doctor_id != current_user_id:
            return jsonify({'error': 'Solo puedes editar tus propias fichas clínicas'}), 403
        
        # Actualizar campos si están presentes
        if 'visit_date' in data:
            record.visit_date = datetime.fromisoformat(data['visit_date'])
        if 'symptoms' in data:
            record.symptoms = data['symptoms']
        if 'diagnosis' in data:
            record.diagnosis = data['diagnosis']
        if 'treatment' in data:
            record.treatment = data['treatment']
        if 'prescriptions' in data:
            record.prescriptions = data['prescriptions']
        if 'observations' in data:  # CORREGIDO: mapear 'observations' a 'notes'
            record.notes = data['observations']
        if 'blood_pressure' in data:
            record.blood_pressure = data['blood_pressure']
        if 'heart_rate' in data:
            record.heart_rate = int(data['heart_rate']) if data['heart_rate'] and data['heart_rate'] != '' else None
        if 'temperature' in data:
            record.temperature = float(data['temperature']) if data['temperature'] and data['temperature'] != '' else None
        if 'weight' in data:
            record.weight = float(data['weight']) if data['weight'] and data['weight'] != '' else None
        if 'height' in data:
            record.height = float(data['height']) if data['height'] and data['height'] != '' else None
        if 'next_appointment' in data:
            record.next_appointment = datetime.fromisoformat(data['next_appointment']) if data['next_appointment'] and data['next_appointment'] != '' else None
        
        # Recalcular IMC si se actualizaron peso o altura
        if record.weight and record.height:
            try:
                height_m = record.height / 100  # convertir cm a metros
                record.bmi = round(record.weight / (height_m ** 2), 1)
            except ZeroDivisionError:
                record.bmi = None
        
        db.session.commit()
        
        return jsonify({
            'message': 'Ficha clínica actualizada exitosamente',
            'clinical_record': record.to_dict()
        })
        
    except ValueError as ve:
        db.session.rollback()
        return jsonify({'error': f'Error en formato de datos: {str(ve)}'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@clinical_records_bp.route('/<int:record_id>', methods=['DELETE'])
@jwt_required()
@role_required('administrador')  # CORREGIDO: usar 'administrador' no 'admin'
def delete_clinical_record(record_id):
    try:
        record = ClinicalRecord.query.get_or_404(record_id)
        db.session.delete(record)
        db.session.commit()
        return jsonify({'message': 'Ficha clínica eliminada exitosamente'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500