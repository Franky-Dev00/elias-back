from models.db import db                # Importa la instancia de la base de datos SQLAlchemy
from datetime import datetime           # Importa la clase datetime para manejar fechas y horas
from werkzeug.security import generate_password_hash, check_password_hash # Para encriptar las claves

class User(db.Model):                   # Define el modelo User que representa la tabla 'user' en la base de datos
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # Identificador único, clave primaria, se autoincrementa
    mail = db.Column(db.String(120), unique=True, nullable=False)     # Email del usuario, debe ser único y obligatorio
    password_hash = db.Column(db.String(200), nullable=False)              # Contraseña del usuario, obligatoria. Incluye hash para no guardar plano
    full_name = db.Column(db.String(120), nullable=False)             # Nombre completo del usuario, obligatorio
    role = db.Column(db.String(50), nullable=False, default="usuario")# Rol del usuario
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)  # Fecha de creación, se asigna automáticamente
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)  # Fecha de última actualización, se actualiza automáticamente
    

    def set_password(self, password):
        # Generar un hash seguro a partir de la contraseña en texto plano
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        # Verifica que la contraseña ingresada coincida con el hash almacenado
        return check_password_hash(self.password_hash, password)