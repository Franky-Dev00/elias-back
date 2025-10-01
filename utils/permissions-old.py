from flask_jwt_extended import get_jwt_identity
from flask import jsonify
from functools import wraps
from models.user import User

def role_required(*roles_permitidos):
    """
    Decorador para proteger rutas según el rol del usuario.
    Uso:
    @role_required('admin')
    @role_required('admin', 'medico')
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                user_id = get_jwt_identity()            # Obtiene el ID del usuario desde el token JWT
                user = User.query.get(user_id)

                if not user:
                    return jsonify({"error": "Usuario no encontrado"}), 404

                if user.role not in roles_permitidos:               # Verifica si el rol del usuario está permitido
                    return jsonify({"error": "No tienes permiso para realizar esta acción"}), 403

                return func(*args, **kwargs)

            except Exception as e:
                return jsonify({"error": str(e)}), 500

        return wrapper
    return decorator
