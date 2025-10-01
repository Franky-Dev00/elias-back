from flask import Blueprint, request, jsonify
from models.responsible import Responsible
from models.db import db
from models.task import Task
from flask_jwt_extended import jwt_required
from utils.permissions import role_required     # Importa los roles y permisos del personal

# SOLO UNA definición del Blueprint
responsibles_bp = Blueprint('responsibles', __name__, url_prefix='/responsibles')

def serialize_responsible(r):
    """Función helper para serializar responsables"""
    return {
        'id': r.id,
        'user_id': r.user_id,
        'area': r.area,
        'created_at': r.created_at.isoformat() if r.created_at else None,
        'updated_at': r.updated_at.isoformat() if r.updated_at else None,
    }

def serialize_task(t):
    """Función helper para serializar tareas"""
    return {
        'id': t.id,
        'title': t.title,
        'done': t.done,
        'responsible_id': t.responsible_id,
        'created_at': t.created_at.isoformat() if t.created_at else None,
        'updated_at': t.updated_at.isoformat() if t.updated_at else None,
    }

# Endpoint 1: Listar todos los responsables
@responsibles_bp.route('/', methods=['GET'])
@jwt_required()
def get_responsibles():
    try:
        responsibles = Responsible.query.all()
        return jsonify([serialize_responsible(r) for r in responsibles])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Endpoint 2: Obtener UN responsable específico
@responsibles_bp.route('/<int:responsible_id>', methods=['GET'])
@jwt_required()
def get_responsible(responsible_id):
    try:
        responsible = Responsible.query.get_or_404(responsible_id)
        return jsonify(serialize_responsible(responsible))          # Devuelve el responsable
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Endpoint 3: Obtener tareas de un responsable (con filtro opcional)
@responsibles_bp.route('/<int:responsible_id>/tasks', methods=['GET'])
@jwt_required()
def get_responsible_tasks(responsible_id):
    try:
        # Verificar que el responsable existe
        Responsible.query.get_or_404(responsible_id)
        
        # Construir query base
        query = Task.query.filter_by(responsible_id=responsible_id)
        
        # Aplicar filtro si existe
        done_param = request.args.get('done')
        if done_param:
            dp = done_param.lower()
            if dp in ['1', 'true', 'yes']:
                query = query.filter_by(done=True)
            elif dp in ['0', 'false', 'no']:
                query = query.filter_by(done=False)
            else:
                return jsonify({"error": "Parámetro done inválido. Use true/false."}), 400
        
        tasks = query.all()
        return jsonify([serialize_task(t) for t in tasks])
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Endpoints POST
@responsibles_bp.route('/', methods=['POST'])
@jwt_required()
@role_required('administrador')                         # Solo administrador puede crear usuarios
def create_responsible():
    try:
        data = request.json
        responsible = Responsible(
            user_id=data['user_id'],
            area=data['area']
        )
        db.session.add(responsible)
        db.session.commit()
        return jsonify({
            'message': 'Responsable creado exitosamente',
            'id': responsible.id
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Endpoints PUT
@responsibles_bp.route('/<int:responsible_id>', methods=['PUT'])
@jwt_required()
def update_responsible(responsible_id):
    try:
        responsible = Responsible.query.get_or_404(responsible_id)
        data = request.json
        
        if 'user_id' in data:
            responsible.user_id = data['user_id']
        if 'area' in data:
            responsible.area = data['area']
        
        db.session.commit()
        return jsonify({
            'message': 'Responsable actualizado exitosamente',
            'responsible': serialize_responsible(responsible)
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Endpoints DELETE
@responsibles_bp.route('/<int:responsible_id>', methods=['DELETE'])
@jwt_required()
@role_required('administrador')                                         # Solo administrador puede eliminar usuarios
def delete_responsible(responsible_id):
    try:
        responsible = Responsible.query.get_or_404(responsible_id)
        db.session.delete(responsible)
        db.session.commit()
        return jsonify({'message': 'Responsable eliminado exitosamente'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
