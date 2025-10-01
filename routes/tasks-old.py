from flask import Blueprint, request, jsonify  # Importa módulos de Flask para crear rutas y manejar peticiones/respuestas JSON
from models.task import Task                   # Importa el modelo Task desde la carpeta models
from models.db import db                       # Importa la instancia de la base de datos

tasks_bp = Blueprint('tasks', __name__, url_prefix='/tasks')  # Crea un blueprint para agrupar las rutas de tareas bajo /tasks

# Obtener todas las tareas desde la base de datos
@tasks_bp.route("/", methods=["GET"])
def get_tasks():
    try:
        tasks = Task.query.all()  # Obtiene todas las tareas de la base de datos
        return jsonify([{
            "id": task.id,                      # ID de la tarea
            "title": task.title,                # Título de la tarea
            "done": task.done,                  # Estado de la tarea (realizada o no)
            "responsible_id": task.responsible_id,  # ID del responsable asociado
            "created_at": task.created_at,      # Fecha de creación
            "updated_at": task.updated_at       # Fecha de última actualización
        } for task in tasks])                   # Devuelve la lista de tareas en formato JSON
    except Exception as e:
        return jsonify({"error": str(e)}), 500  # Si ocurre un error, devuelve el mensaje en formato JSON y código 500

# Obtener una tarea por su ID
@tasks_bp.route("/<int:task_id>", methods=["GET"])
def get_task(task_id):
    try:
        task = Task.query.get_or_404(task_id)   # Busca la tarea por ID, devuelve 404 si no existe
        return jsonify({
            "id": task.id,
            "title": task.title,
            "done": task.done,
            "responsible_id": task.responsible_id,
            "created_at": task.created_at,
            "updated_at": task.updated_at
        })  # Devuelve los datos de la tarea en formato JSON
    except Exception as e:
        return jsonify({"error": str(e)}), 500  # Devuelve el error en formato JSON y código 500

# Crear nueva tarea en la base de datos
@tasks_bp.route("/", methods=["POST"])
def create_task():
    try:
        data = request.get_json()  # Obtiene los datos enviados en formato JSON
        new_task = Task(
            title=data.get("title"),                # Asigna el título de la tarea
            done=data.get("done", False),           # Asigna el estado, por defecto False
            responsible_id=data.get("responsible_id")  # Asigna el ID del responsable
        )
        db.session.add(new_task)                    # Agrega la tarea a la sesión de la base de datos
        db.session.commit()                         # Guarda los cambios en la base de datos
        return jsonify({
            "id": new_task.id,
            "title": new_task.title,
            "done": new_task.done,
            "responsible_id": new_task.responsible_id,
            "created_at": new_task.created_at,
            "updated_at": new_task.updated_at
        }), 201  # Devuelve los datos de la tarea creada y código 201 (creado)
    except Exception as e:
        db.session.rollback()                       # Revierte la transacción si ocurre un error
        return jsonify({"error": str(e)}), 500      # Devuelve el error en formato JSON y código 500

# Actualizar tarea en la base de datos
@tasks_bp.route("/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    try:
        task = Task.query.get_or_404(task_id)       # Busca la tarea por ID, devuelve 404 si no existe
        data = request.get_json()                   # Obtiene los datos enviados en formato JSON
        task.title = data.get("title", task.title)  # Actualiza el título si se envía, si no, mantiene el actual
        task.done = data.get("done", task.done)     # Actualiza el estado si se envía
        task.responsible_id = data.get("responsible_id", task.responsible_id)  # Actualiza el responsable si se envía
        db.session.commit()                         # Guarda los cambios en la base de datos
        return jsonify({
            "id": task.id,
            "title": task.title,
            "done": task.done,
            "responsible_id": task.responsible_id,
            "created_at": task.created_at,
            "updated_at": task.updated_at
        })  # Devuelve los datos de la tarea actualizada en formato JSON
    except Exception as e:
        db.session.rollback()                       # Revierte la transacción si ocurre un error
        return jsonify({"error": str(e)}), 500      # Devuelve el error en formato JSON y código 500

# Eliminar tarea en la base de datos
@tasks_bp.route("/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    try:
        task = Task.query.get_or_404(task_id)       # Busca la tarea por ID, devuelve 404 si no existe
        db.session.delete(task)                     # Elimina la tarea de la base de datos
        db.session.commit()                         # Guarda los cambios en la base de datos
        return jsonify({"message": "Tarea eliminada"})  # Devuelve mensaje de éxito
    except Exception as e:
        db.session.rollback()                       # Revierte la transacción si ocurre un error
        return jsonify({"error": str(e)}), 500      # Devuelve el error en formato JSON y código 500