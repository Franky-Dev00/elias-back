from flask import Blueprint, request, jsonify
from models.user import User
from models.db import db
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from utils.permissions import role_required
from sqlalchemy import func

users_bp = Blueprint('users', __name__, url_prefix='/users')

def serialize_user(user):
    return {
        'id': user.id,
        'mail': user.mail,
        'full_name': user.full_name,
        'role': user.role,
        'created_at': user.created_at.isoformat() if user.created_at else None,
        'updated_at': user.updated_at.isoformat() if user.updated_at else None
    }

@users_bp.route('/', methods=['GET'])
@jwt_required()
@role_required('administrador')
def get_users():
    """Obtener todos los usuarios - Solo administrador"""
    try:
        users = User.query.order_by(User.created_at.desc()).all()
        return jsonify([serialize_user(user) for user in users])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@users_bp.route('/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    """Obtener un usuario específico"""
    try:
        current_user_id = int(get_jwt_identity())
        current_user = User.query.get(current_user_id)
        
        # Solo administrador o el mismo usuario pueden ver detalles
        if current_user.role != 'administrador' and current_user_id != user_id:
            return jsonify({'error': 'No tienes permiso para ver este usuario'}), 403
        
        user = User.query.get_or_404(user_id)
        return jsonify(serialize_user(user))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@users_bp.route('/stats', methods=['GET'])
@jwt_required()
@role_required('administrador')
def get_users_stats():
    """Obtener estadísticas de usuarios"""
    try:
        total_users = User.query.count()
        
        # Usuarios por rol
        users_by_role = db.session.query(
            User.role,
            func.count(User.id).label('count')
        ).group_by(User.role).all()
        
        role_distribution = {role: count for role, count in users_by_role}
        
        # Usuarios recientes (últimos 7 días)
        from datetime import timedelta
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent_users = User.query.filter(User.created_at >= week_ago).count()
        
        return jsonify({
            'total_users': total_users,
            'role_distribution': role_distribution,
            'recent_users': recent_users
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@users_bp.route('/', methods=['POST'])
@jwt_required()
@role_required('administrador')
def create_user():
    """Crear nuevo usuario - Solo administrador"""
    try:
        data = request.json
        
        # Validaciones
        if not data.get('mail'):
            return jsonify({'error': 'El email es obligatorio'}), 400
        if not data.get('password'):
            return jsonify({'error': 'La contraseña es obligatoria'}), 400
        if not data.get('full_name'):
            return jsonify({'error': 'El nombre completo es obligatorio'}), 400
        if not data.get('role'):
            return jsonify({'error': 'El rol es obligatorio'}), 400
        
        # Validar rol válido
        valid_roles = ['administrador', 'medico', 'tecnico', 'administrativo']
        if data['role'] not in valid_roles:
            return jsonify({'error': f'Rol inválido. Roles permitidos: {", ".join(valid_roles)}'}), 400
        
        # Verificar si el email ya existe
        if User.query.filter_by(mail=data['mail']).first():
            return jsonify({'error': 'El email ya está registrado'}), 400
        
        # Validar formato de email
        if '@' not in data['mail'] or '.' not in data['mail']:
            return jsonify({'error': 'Formato de email inválido'}), 400
        
        # Validar longitud de contraseña
        if len(data['password']) < 6:
            return jsonify({'error': 'La contraseña debe tener al menos 6 caracteres'}), 400
        
        user = User(
            mail=data['mail'],
            full_name=data['full_name'],
            role=data['role']
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
@jwt_required()
def update_user(user_id):
    """Actualizar usuario"""
    try:
        current_user_id = int(get_jwt_identity())
        current_user = User.query.get(current_user_id)
        user = User.query.get_or_404(user_id)
        data = request.json

        # Solo administrador o el mismo usuario pueden editar
        if current_user.role != 'administrador' and current_user_id != user_id:
            return jsonify({'error': 'Solo puedes editar tu propio perfil'}), 403
        
        # Solo administrador puede cambiar roles
        if 'role' in data and current_user.role != 'administrador':
            return jsonify({'error': 'Solo administradores pueden cambiar roles'}), 403
        
        # Validar email único si se está actualizando
        if 'mail' in data and data['mail'] != user.mail:
            if User.query.filter_by(mail=data['mail']).first():
                return jsonify({'error': 'El email ya está en uso'}), 400
        
        # Actualizar campos
        if 'mail' in data:
            user.mail = data['mail']
        if 'full_name' in data:
            user.full_name = data['full_name']
        if 'role' in data and current_user.role == 'administrador':
            user.role = data['role']
        if 'password' in data:
            if len(data['password']) < 6:
                return jsonify({'error': 'La contraseña debe tener al menos 6 caracteres'}), 400
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
@jwt_required()
@role_required('administrador')
def delete_user(user_id):
    """Eliminar usuario - Solo administrador"""
    try:
        current_user_id = int(get_jwt_identity())
        
        # No permitir que administrador se elimine a sí mismo
        if current_user_id == user_id:
            return jsonify({'error': 'No puedes eliminar tu propia cuenta'}), 400
        
        user = User.query.get_or_404(user_id)
        
        # Verificar si el usuario tiene registros asociados (advertencia)
        # Nota: Con el diseño actual, no hay problema por información inmutable
        
        db.session.delete(user)
        db.session.commit()
        return jsonify({'message': f'Usuario {user.full_name} eliminado exitosamente'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@users_bp.route('/roles', methods=['GET'])
@jwt_required()
@role_required('administrador')
def get_available_roles():
    """Obtener roles disponibles en el sistema"""
    try:
        roles = [
            {'value': 'administrador', 'label': 'Administrador'},
            {'value': 'medico', 'label': 'Médico'},
            {'value': 'tecnico', 'label': 'Técnico'},
            {'value': 'administrativo', 'label': 'Administrativo'}
        ]
        return jsonify(roles)
    except Exception as e:
        return jsonify({'error': str(e)}), 500