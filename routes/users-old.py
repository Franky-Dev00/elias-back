from flask import Blueprint, request, jsonify   # Importa módulos de Flask para crear rutas y manejar peticiones/respuestas JSON
from models.user import User                    # Importa el modelo User desde la carpeta models
from models.db import db                        # Importa la instancia de la base de datos
from flask_jwt_extended import jwt_required     # importa Protección JWT
from datetime import datetime                   #
from utils.permissions import role_required     # 

users_bp = Blueprint('users', __name__, url_prefix='/users')

def serialize_user(user):                                       #Función helper para serializar usuarios    
    return {
        'id': user.id,                                          # ID del usuario
        'mail': user.mail,                                      # Email del usuario
        'full_name': user.full_name,                            # Nombre completo
        'role': user.role,                                      # Rol del usuario
        'created_at': user.created_at.isoformat() if user.created_at else None,
        'updated_at': user.updated_at.isoformat() if user.updated_at else None
    }

@users_bp.route('/', methods=['GET'])
@jwt_required()                                     # Protegido
def get_users():
    try:
        users = User.query.all()
        return jsonify([serialize_user(user) for user in users])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@users_bp.route('/<int:user_id>', methods=['GET'])
@jwt_required()                                     # Protegido
def get_user(user_id):
    try:
        user = User.query.get_or_404(user_id)
        return jsonify(serialize_user(user))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@users_bp.route('/', methods=['POST'])
@jwt_required()                                     # Protegido (solo admin puede crear usuarios)
@role_required('administrador')                          # Solo admin puede crear usuarios
def create_user():
    try:
        data = request.json
        
        # Validaciones
        if not data.get('mail'):
            return jsonify({'error': 'El email es obligatorio'}), 400
        if not data.get('password'):
            return jsonify({'error': 'La contraseña es obligatoria'}), 400
        if not data.get('full_name'):
            return jsonify({'error': 'El nombre completo es obligatorio'}), 400
        
        # Verificar si el email ya existe
        if User.query.filter_by(mail=data['mail']).first():
            return jsonify({'error': 'El email ya está registrado'}), 400
        
        user = User(
            mail=data['mail'],
            full_name=data['full_name'],
            role=data.get('role', 'usuario')
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            'message': 'Usuario creado exitosamente',
            'user': serialize_user(user)
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@users_bp.route('/<int:user_id>', methods=['PUT'])
@jwt_required()                                           # Protegido
def update_user(user_id):
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get_or_404(user_id)
        data = request.json

        if current_user_id != user_id and User.query.get(current_user_id).role != 'admin':  # Permite que usuarios editen solo su propio perfil, excepto admin
            return jsonify({'error': 'Solo puedes editar tu propio perfil'}), 403
        
        # Validar email único si se está actualizando
        if 'mail' in data and data['mail'] != user.mail:
            if User.query.filter_by(mail=data['mail']).first():
                return jsonify({'error': 'El email ya está en uso'}), 400
        
        # Actualizar campos
        if 'mail' in data:
            user.mail = data['mail']
        if 'full_name' in data:
            user.full_name = data['full_name']
        if 'role' in data:
            user.role = data['role']
        if 'password' in data:
            user.set_password(data['password'])
        
        db.session.commit()
        
        return jsonify({
            'message': 'Usuario actualizado exitosamente',
            'user': serialize_user(user)
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@users_bp.route('/<int:user_id>', methods=['DELETE'])
@jwt_required()                                             # Protegido (solo admin)
@role_required('administrador')                                 # Solo admin puede eliminar usuarios
def delete_user(user_id):
    try:
        user = User.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        return jsonify({'message': 'Usuario eliminado exitosamente'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500