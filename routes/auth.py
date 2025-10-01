from flask import Blueprint, request, jsonify
from models.user import User
from models.db import db
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity  # Acá importo JWT para generar el token

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.json
        mail = data.get('mail')
        password_hash = data.get('password')

        if not mail or not password_hash:
            return jsonify({"error": "Mail y contraseña son obligatorios"}), 400  # Validar campos obligatorios

        user = User.query.filter_by(mail=mail).first()
        if user and user.check_password(password_hash):
            access_token = create_access_token(identity=str(user.id))  # Genera el token JWT con la identidad usuario, además es string

            return jsonify({                           # En esta primera versión solo devolvemos datos básicos
                "message": "Login exitoso",            
                "access_token": access_token,          # Aquí se envía el token al cliente
                "token_type": "bearer",               # Añadimos tipo de token
                "user": {
                    "id": user.id,
                    "mail": user.mail,
                    "full_name": user.full_name,
                    "role": user.role
                }
            }), 200
        else:
            return jsonify({"error": "Credenciales inválidas"}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/verify', methods=['GET'])                  # Endpoint para verificar token
@jwt_required()
def verify_token():
    try:                                                    # Endpoint para verificar si el token es válido
        user_id = int(get_jwt_identity())                   # convertido a Entero para la consulta
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({"error": "Usuario no encontrado"}), 404
            
        return jsonify({
            "message": "Token válido",
            "user": {
                "id": user.id,
                "mail": user.mail,
                "full_name": user.full_name,
                "role": user.role
            }
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500