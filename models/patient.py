from models.db import db        # Importa la instancia de la base de datos SQLAlchemy.
from datetime import datetime         # Importa la clase datetime para manejar fechas y horas

class Patient(db.Model):
    __tablename__ = 'patient'
    
    id = db.Column(db.Integer, primary_key=True)
    rut = db.Column(db.String(12), unique=True, nullable=False)     # Formato: 12345678-9
    full_name = db.Column(db.String(120), nullable=False)
    birth_date = db.Column(db.Date, nullable=False)
    gender = db.Column(db.String(10), nullable=False)               # 'male', 'female', 'other'
    address = db.Column(db.Text)
    phone = db.Column(db.String(20))                                # No obligatorio como solicitaste
    email = db.Column(db.String(120))
    emergency_contact = db.Column(db.String(120))
    emergency_phone = db.Column(db.String(20))
    blood_type = db.Column(db.String(5))                            # 'A+', 'O-', etc.
    allergies = db.Column(db.Text)                                  # Alergias conocidas
    chronic_diseases = db.Column(db.Text)                           # Enfermedades crónicas
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relación con fichas clínicas
    clinical_records = db.relationship('ClinicalRecord', back_populates='patient', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Patient {self.rut} - {self.full_name}>'

    def to_dict(self):
        return {                                            # Serializar paciente a diccionario
            'id': self.id,
            'rut': self.rut,
            'full_name': self.full_name,
            'birth_date': self.birth_date.isoformat() if self.birth_date else None,
            'gender': self.gender,
            'address': self.address,
            'phone': self.phone,
            'email': self.email,
            'emergency_contact': self.emergency_contact,
            'emergency_phone': self.emergency_phone,
            'blood_type': self.blood_type,
            'allergies': self.allergies,
            'chronic_diseases': self.chronic_diseases,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }