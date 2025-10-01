from flask import Blueprint, request, jsonify
from datetime import datetime
from models import Patient, db
from flask_jwt_extended import jwt_required, get_jwt_identity
from utils.permissions import role_required

patients_bp = Blueprint('patients', __name__, url_prefix='/patients')

@patients_bp.route('/', methods=['GET'])
@jwt_required()
def get_patients():
    try:
        patients = Patient.query.all()
        return jsonify([patient.to_dict() for patient in patients])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@patients_bp.route('/<int:patient_id>', methods=['GET'])
@jwt_required()
def get_patient(patient_id):
    try:
        patient = Patient.query.get_or_404(patient_id)
        return jsonify(patient.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@patients_bp.route('/', methods=['POST'])
@jwt_required()
@role_required('admin', 'medico', 'tecnico')
def create_patient():
    try:
        data = request.json
        
        # Validaciones básicas
        if not data.get('rut'):
            return jsonify({'error': 'El RUT es obligatorio'}), 400
        if not data.get('full_name'):
            return jsonify({'error': 'El nombre completo es obligatorio'}), 400
        if not data.get('birth_date'):
            return jsonify({'error': 'La fecha de nacimiento es obligatoria'}), 400
        if not data.get('gender'):
            return jsonify({'error': 'El género es obligatorio'}), 400
        
        # Verificar si el RUT ya existe
        if Patient.query.filter_by(rut=data['rut']).first():
            return jsonify({'error': 'El RUT ya está registrado'}), 400
        
        patient = Patient(
            rut=data['rut'],
            full_name=data['full_name'],
            birth_date=datetime.fromisoformat(data['birth_date']),
            gender=data['gender'],
            address=data.get('address'),
            phone=data.get('phone'),
            email=data.get('email'),
            emergency_contact=data.get('emergency_contact'),
            emergency_phone=data.get('emergency_phone'),
            blood_type=data.get('blood_type'),
            allergies=data.get('allergies'),
            chronic_diseases=data.get('chronic_diseases')
        )
        
        db.session.add(patient)
        db.session.commit()
        
        return jsonify({
            'message': 'Paciente creado exitosamente',
            'patient': patient.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@patients_bp.route('/<int:patient_id>', methods=['PUT'])
@jwt_required()
@role_required('admin', 'medico', 'tecnico')
def update_patient(patient_id):
    try:
        patient = Patient.query.get_or_404(patient_id)
        data = request.json
        
        # Validar RUT único si se está actualizando
        if 'rut' in data and data['rut'] != patient.rut:
            if Patient.query.filter_by(rut=data['rut']).first():
                return jsonify({'error': 'El RUT ya está en uso'}), 400
        
        # Actualizar campos
        if 'rut' in data:
            patient.rut = data['rut']
        if 'full_name' in data:
            patient.full_name = data['full_name']
        if 'birth_date' in data:
            patient.birth_date = datetime.fromisoformat(data['birth_date'])
        if 'gender' in data:
            patient.gender = data['gender']
        if 'address' in data:
            patient.address = data['address']
        if 'phone' in data:
            patient.phone = data['phone']
        if 'email' in data:
            patient.email = data['email']
        if 'emergency_contact' in data:
            patient.emergency_contact = data['emergency_contact']
        if 'emergency_phone' in data:
            patient.emergency_phone = data['emergency_phone']
        if 'blood_type' in data:
            patient.blood_type = data['blood_type']
        if 'allergies' in data:
            patient.allergies = data['allergies']
        if 'chronic_diseases' in data:
            patient.chronic_diseases = data['chronic_diseases']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Paciente actualizado exitosamente',
            'patient': patient.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@patients_bp.route('/<int:patient_id>', methods=['DELETE'])
@jwt_required()
@role_required('admin')
def delete_patient(patient_id):
    try:
        patient = Patient.query.get_or_404(patient_id)
        db.session.delete(patient)
        db.session.commit()
        return jsonify({'message': 'Paciente eliminado exitosamente'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500