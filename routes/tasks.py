from flask import Blueprint, request, jsonify
from models.task import Task
from models.db import db
from models.responsible import Responsible                      # Para validar que el responsable existe
from flask_jwt_extended import jwt_required, get_jwt_identity   # Para proteger los endpoints
from utils.permissions import role_required                     # Importa role requerido para permisos del admin

tasks_bp = Blueprint('tasks', __name__, url_prefix='/tasks')

# Función helper para serializar tareas
def serialize_task(task):
    return {
        "id": task.id,
        "title": task.title,
        "done": task.done,
        "responsible_id": task.responsible_id,
        "created_at": task.created_at.isoformat() if task.created_at else None,
        "updated_at": task.updated_at.isoformat() if task.updated_at else None,
    }

# Obtener todas las tareas
@tasks_bp.route("/", methods=["GET"])
@jwt_required()                           # Protegido con JWT
def get_tasks():
    try:
        tasks = Task.query.all()
        return jsonify([serialize_task(task) for task in tasks])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Obtener una tarea por ID
@tasks_bp.route("/<int:task_id>", methods=["GET"])
@jwt_required()                           # Protegido con JWT
def get_task(task_id):
    try:
        task = Task.query.get_or_404(task_id)
        return jsonify(serialize_task(task))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Crear nueva tarea
@tasks_bp.route("/", methods=["POST"])
@jwt_required()                           # Protegido con JWT
@role_required('administrador', 'medico')         # Permite al administrador o medico crear
def create_task():
    try:
        data = request.json
        
        # Validaciones
        if not data.get("title"):
            return jsonify({"error": "El título es obligatorio"}), 400
        
        if not data.get("responsible_id"):
            return jsonify({"error": "El responsible_id es obligatorio"}), 400
        
        # Verificar que el responsable existe
        responsible = Responsible.query.get(data.get("responsible_id"))
        if not responsible:
            return jsonify({"error": "El responsable especificado no existe"}), 400
        
        new_task = Task(
            title=data.get("title"),
            done=data.get("done", False),
            responsible_id=data.get("responsible_id")
        )
        
        db.session.add(new_task)
        db.session.commit()
        
        return jsonify(serialize_task(new_task)), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# Actualizar tarea
@tasks_bp.route("/<int:task_id>", methods=["PUT"])
@jwt_required()                           # Protegido con JWT
def update_task(task_id):
    try:
        task = Task.query.get_or_404(task_id)
        data = request.json
        
        # Validar responsible_id si se está actualizando
        if "responsible_id" in data and data["responsible_id"] is not None:
            responsible = Responsible.query.get(data["responsible_id"])
            if not responsible:
                return jsonify({"error": "El responsable especificado no existe"}), 400
        
        # Actualizar campos
        if "title" in data:
            task.title = data["title"]
        if "done" in data:
            task.done = data["done"]
        if "responsible_id" in data:
            task.responsible_id = data["responsible_id"]
        
        db.session.commit()
        return jsonify(serialize_task(task))
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# Eliminar tarea
@tasks_bp.route("/<int:task_id>", methods=["DELETE"])
@jwt_required()                           # Protegido con JWT
@role_required('administrador', 'medico')         # Permite al administrador o medico eliminar
def delete_task(task_id):
    try:
        task = Task.query.get_or_404(task_id)
        db.session.delete(task)
        db.session.commit()
        return jsonify({"message": "Tarea eliminada exitosamente"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500