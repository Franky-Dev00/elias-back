from models.db import db                           # Importa la instancia de la base de datos SQLAlchemy
from datetime import datetime                      # Importa la clase datetime para manejar fechas y horas

class ClinicalRecord(db.Model):
    __tablename__ = 'clinical_record'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)         # Médico responsable
    visit_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    symptoms = db.Column(db.Text)                               # Síntomas reportados
    diagnosis = db.Column(db.Text)                              # Diagnóstico
    treatment = db.Column(db.Text)                              # Tratamiento indicado
    prescriptions = db.Column(db.Text)                          # Medicamentos recetados
    notes = db.Column(db.Text)                                  # Observaciones adicionales
    blood_pressure = db.Column(db.String(20))                   # Ej: "120/80"
    heart_rate = db.Column(db.Integer)                          # Latidos por minuto
    temperature = db.Column(db.Float)                           # Temperatura corporal
    weight = db.Column(db.Float)                                # Peso en kg
    height = db.Column(db.Float)                                # Altura en cm
    bmi = db.Column(db.Float)                                   # Índice de masa corporal
    next_appointment = db.Column(db.DateTime)                   # Próxima cita
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    patient = db.relationship('Patient', back_populates='clinical_records')
    doctor = db.relationship('User', back_populates='clinical_records_doctor')

    def __repr__(self):
        return f'<ClinicalRecord {self.id} - Patient {self.patient_id}>'

    def to_dict(self):
        return {                                # Serializar ficha clínica a diccionario
            'id': self.id,
            'patient_id': self.patient_id,
            'doctor_id': self.doctor_id,
            'visit_date': self.visit_date.isoformat() if self.visit_date else None,
            'symptoms': self.symptoms,
            'diagnosis': self.diagnosis,
            'treatment': self.treatment,
            'prescriptions': self.prescriptions,
            'notes': self.notes,
            'blood_pressure': self.blood_pressure,
            'heart_rate': self.heart_rate,
            'temperature': self.temperature,
            'weight': self.weight,
            'height': self.height,
            'bmi': self.bmi,
            'next_appointment': self.next_appointment.isoformat() if self.next_appointment else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'patient_name': self.patient.full_name if self.patient else None,
            'doctor_name': self.doctor.full_name if self.doctor else None
        }