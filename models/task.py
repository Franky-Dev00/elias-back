from models.db import db                       # Importa la instancia de la base de datos SQLAlchemy
from datetime import datetime                  # Importa la clase datetime para manejar fechas y horas

class Task(db.Model):                          # Define el modelo Task que representa la tabla 'task' en la base de datos
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # Identificador único, clave primaria, se autoincrementa
    title = db.Column(db.String(255), nullable=False)                 # Título de la tarea, obligatorio
    done = db.Column(db.Boolean, default=False)                      # Estado de la tarea (realizada o no), por defecto False
    responsible_id = db.Column(db.Integer, db.ForeignKey('responsible.id'), nullable=False)  # Clave foránea a Responsible, obligatorio
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)             # Fecha de creación, se asigna automáticamente
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)  # Fecha de última actualización, se actualiza automáticamente
    
    responsible = db.relationship('Responsible', backref='tasks')    # Relación muchos a uno; permite acceder al responsable desde la tarea y a todas las tareas desde el responsable