from models.db import db                    # Importa la instancia de la base de datos SQLAlchemy
from datetime import datetime               # Importa la clase datetime para manejar fechas y horas

class Responsible(db.Model):                # Define el modelo Responsible que representa la tabla 'responsible' en la base de datos
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # Identificador único, clave primaria, se autoincrementa
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)  # Clave foránea a User, única para relación 1 a 1, obligatoria
    area = db.Column(db.String(120), nullable=False)                  # Área del responsable, obligatorio
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)  # Fecha de creación, se asigna automáticamente
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)  # Fecha de última actualización, se actualiza automáticamente
    
    user = db.relationship('User', backref='responsible', uselist=False) # Relación uno a uno con User; permite acceder al usuario desde Responsible y viceversa