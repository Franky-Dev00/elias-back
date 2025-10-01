from flask import Blueprint, request, jsonify  # Importa módulos de Flask para rutas y manejo de peticiones/respuestas JSON
from models.responsible import Responsible     # Importa el modelo Responsible
from models.db import db                      # Importa la instancia de la base de datos
from models.task import Task                  # Para considera un endpoint
from models.responsible import Responsible      # importa el modelo


responsibles_bp = Blueprint('responsibles', __name__, url_prefix='/responsibles')  # Crea un blueprint para agrupar las rutas bajo /responsibles

@responsibles_bp.route('/', methods=['GET'])
def get_responsibles():
    try:
        responsibles = Responsible.query.all()  # Obtiene todos los responsables de la base de datos
        return jsonify([{
            'id': r.id,                        # ID del responsable
            'user_id': r.user_id,              # ID de usuario asociado
            'area': r.area,                    # Área del responsable
            'created_at': r.created_at,        # Fecha de creación
            'updated_at': r.updated_at         # Fecha de última actualización
        } for r in responsibles])              # Devuelve la lista en formato JSON
    except Exception as e:
        return jsonify({'error': str(e)}), 500  # Devuelve el error en formato JSON y código 500

@responsibles_bp.route('/<int:responsible_id>', methods=['GET'])
def get_responsible(responsible_id):
    try:
        r = Responsible.query.get_or_404(responsible_id)  # Busca el responsable por ID, devuelve 404 si no existe

        done_param = request.args.get('done', None)       # Permitir filtro opcional ?done=true|false
        if done_param is not None:
            dp = done_param.lower()
            if dp in ['1', 'true', 'yes']:
                tasks = Task.query.filter_by(responsible_id=r.id, done=True).all()
            elif dp in ['0', 'false', 'no']:
                tasks = Task.query.filter_by(responsible_id=r.id, done=False).all()
            else:
                return jsonify({"error": "Parámetro done inválido. Use true/false."}), 400
        else:
            tasks = Task.query.filter_by(responsible_id=r.id).all()

        return jsonify([{       # Serializar y devolver
            'id': r.id,
            'user_id': r.user_id,
            'done': t.done,
            'responsible_id': t.responsible_id,
            'created_at': r.created_at,
            'updated_at': r.updated_at
        } for t in tasks])  # Devuelve los datos del responsable en formato JSON

    except Exception as e:
        return jsonify({'error': str(e)}), 500  # Devuelve el error en formato JSON y código 500

@responsibles_bp.route('/<int:responsible_id>/tasks', methods=['GET']) # nuevo elemento para devolver solo tareas, sin info del responsable
def get_responsible_tasks(responsible_id):
    try:
        tasks = Task.query.filter_by(responsible_id=responsible_id).all()

        done_param = request.args.get('done', None)
        if done_param is not None:
            dp = done_param.lower()
            if dp in ['1', 'true', 'yes']:
                tasks = Task.query.filter_by(responsible_id=responsible_id, done=True).all()
            elif dp in ['0', 'false', 'no']:
                tasks = Task.query.filter_by(responsible_id=responsible_id, done=False).all()
            else:
                return jsonify({"error": "Parámetro done inválido. Use true/false."}), 400
        else:
            tasks = Task.query.filter_by(responsible_id=responsible_id).all()

        return jsonify([{
            "id": t.id,
            "title": t.title,
            "done": t.done,
            "responsible_id": t.responsible_id,
            "created_at": t.created_at,
            "updated_at": t.updated_at
        } for t in tasks])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

from flask import Blueprint, jsonify
from models.db import db
from models.responsible import Responsible  # importa el modelo

responsibles_bp = Blueprint("responsibles_bp", __name__)

# --- NUEVO: GET para listar responsables ---
@responsibles_bp.route("/responsibles", methods=["GET"])
def get_responsibles():
    try:
        responsibles = Responsible.query.all()
        return jsonify([
            {
                "id": r.id,
                "user_id": r.user_id,
                "area": r.area,
                "created_at": r.created_at.isoformat() if r.created_at else None,
                "updated_at": r.updated_at.isoformat() if r.updated_at else None,
            }
            for r in responsibles
        ])
    except Exception as e:
        return jsonify({"error": str(e)}), 500
# ---------------------------------------------------------------------------------------

@responsibles_bp.route('/', methods=['POST'])
def create_responsible():
    try:
        data = request.json  # Obtiene los datos enviados en formato JSON
        responsible = Responsible(
            user_id=data['user_id'],  # Asigna el ID de usuario
            area=data['area']         # Asigna el área
        )
        db.session.add(responsible)   # Agrega el responsable a la sesión de la base de datos
        db.session.commit()           # Guarda los cambios en la base de datos
        return jsonify({'id': responsible.id}), 201  # Devuelve el ID del responsable creado y código 201 (creado)
    except Exception as e:
        db.session.rollback()         # Revierte la transacción si ocurre un error
        return jsonify({'error': str(e)}), 500  # Devuelve el error en formato JSON y código 500

@responsibles_bp.route('/<int:responsible_id>', methods=['PUT'])
def update_responsible(responsible_id):
    try:
        responsible = Responsible.query.get_or_404(responsible_id)  # Busca el responsable por ID, devuelve 404 si no existe
        data = request.json  # Obtiene los datos enviados en formato JSON
        responsible.user_id = data.get('user_id', responsible.user_id)  # Actualiza el ID de usuario si se envía
        responsible.area = data.get('area', responsible.area)           # Actualiza el área si se envía
        db.session.commit()  # Guarda los cambios en la base de datos
        return jsonify({'message': 'Responsible updated'})  # Devuelve mensaje de éxito
    except Exception as e:
        db.session.rollback()  # Revierte la transacción si ocurre un error
        return jsonify({'error': str(e)}), 500  # Devuelve el error en formato JSON y código 500

@responsibles_bp.route('/<int:responsible_id>', methods=['DELETE'])
def delete_responsible(responsible_id):
    try:
        responsible = Responsible.query.get_or_404(responsible_id)  # Busca el responsable por ID, devuelve 404 si no existe
        db.session.delete(responsible)  # Elimina el responsable de la base de datos
        db.session.commit()             # Guarda los cambios en la base de datos
        return jsonify({'message': 'Responsible deleted'})  # Devuelve mensaje de éxito
    except Exception as e:
        db.session.rollback()  # Revierte la transacción si ocurre un error
        return jsonify({'error': str(e)}), 500  # Devuelve el error en formato JSON y código 500