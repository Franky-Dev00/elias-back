from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

DATABASE_URL = 'postgresql://elias:CMG3_elias$@44.199.207.193:5432/elias'
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy()

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(255), nullable=False)
    done = db.Column(db.Boolean, default=False)

db.init_app(app)

# Ruta de inicio
@app.route("/")
def home():
    return "Bienvenido a la API de Tareas con Flask"

# Obtener todas las tareas desde la base de datos
@app.route("/tasks", methods=["GET"])
def get_tasks():
    tasks = Task.query.all()
    task_list = []
    for task in tasks:
        task_list.append({
            "id": task.id,
            "title": task.title,
            "done": task.done
        })
    return jsonify(task_list)

# Crear nueva tarea en la base de datos
@app.route("/tasks", methods=["POST"])
def create_task():
    data = request.get_json()
    new_task = Task(
        title=data.get("title"),
        done=data.get("done", False)
    )
    db.session.add(new_task)
    db.session.commit()
    return jsonify({
        "id": new_task.id,
        "title": new_task.title,
        "done": new_task.done
    }), 201

# Actualizar tarea en la base de datos
@app.route("/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    task = Task.query.get(task_id)
    
    if task:
        data = request.get_json()
        task.title = data.get("title", task.title)
        task.done = data.get("done", task.done)
        db.session.commit()
        return jsonify({
            "id": task.id,
            "title": task.title,
            "done": task.done
        }), 200
    return jsonify({"error": "Tarea no encontrada"}), 404

# Eliminar tarea en la base de datos
@app.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    task = Task.query.get(task_id)
    if task:
        db.session.delete(task)
        db.session.commit()
        return jsonify({"message": "Tarea eliminada"}), 200
    return jsonify({"error": "Tarea no encontrada"}), 404

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8083)
