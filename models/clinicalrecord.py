from models.db import db
from datetime import datetime

class ClinicalRecord(db.Model):
    __tablename__ = 'clinical_record'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    
    # INFORMACIÓN INMUTABLE DEL MÉDICO (copiada al crear la ficha)
    doctor_name = db.Column(db.String(120), nullable=False)     # Nombre completo del médico
    doctor_email = db.Column(db.String(120), nullable=False)    # Email del médico al momento de crear
    doctor_role = db.Column(db.String(50), nullable=False)      # Rol del médico (medico, administrador)
    doctor_id_snapshot = db.Column(db.Integer, nullable=True)   # ID original del médico (referencia histórica)
    
    # Información médica opcional (si está disponible)
    doctor_license = db.Column(db.String(50), nullable=True)            # Número de colegiatura
    doctor_specialization = db.Column(db.String(100), nullable=True)    # Especialidad
    
    # Datos clínicos de la consulta
    visit_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    reason_visit = db.Column(db.Text, nullable=False)  # Motivo de la consulta
    symptoms = db.Column(db.Text)                      # Síntomas reportados
    diagnosis = db.Column(db.Text, nullable=False)     # Diagnóstico (obligatorio)
    treatment = db.Column(db.Text)                     # Tratamiento indicado
    prescriptions = db.Column(db.Text)                 # Medicamentos recetados
    notes = db.Column(db.Text)                         # Observaciones adicionales
    
    # Signos vitales
    blood_pressure = db.Column(db.String(20))          # Ej: "120/80"
    heart_rate = db.Column(db.Integer)                 # Latidos por minuto
    temperature = db.Column(db.Float)                  # Temperatura corporal
    weight = db.Column(db.Float)                       # Peso en kg
    height = db.Column(db.Float)                       # Altura en cm
    bmi = db.Column(db.Float)                          # Índice de masa corporal (calculado)
    
    # Seguimiento
    next_appointment = db.Column(db.DateTime)          # Próxima cita
    
    # Auditoría
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relación con paciente (se mantiene solo esta relación)
    patient = db.relationship('Patient', back_populates='clinical_records')
    
    def __repr__(self):
        return f'<ClinicalRecord {self.id} - Patient {self.patient_id} - Dr. {self.doctor_name}>'

    @classmethod
    def create_with_doctor_info(cls, patient_id, doctor_user, clinical_data):
        """
        Método de clase para crear una ficha clínica capturando información inmutable del médico
        """
        return cls(
            patient_id=patient_id,
            # Información inmutable del médico
            doctor_name=doctor_user.full_name,
            doctor_email=doctor_user.mail,
            doctor_role=doctor_user.role,
            doctor_id_snapshot=doctor_user.id,
            doctor_license=getattr(doctor_user, 'medical_license', None),
            doctor_specialization=getattr(doctor_user, 'specialization', None),
            # Datos clínicos
            visit_date=clinical_data.get('visit_date'),
            reason_visit=clinical_data.get('reason_visit'),
            symptoms=clinical_data.get('symptoms'),
            diagnosis=clinical_data.get('diagnosis'),
            treatment=clinical_data.get('treatment'),
            prescriptions=clinical_data.get('prescriptions'),
            notes=clinical_data.get('notes'),
            blood_pressure=clinical_data.get('blood_pressure'),
            heart_rate=clinical_data.get('heart_rate'),
            temperature=clinical_data.get('temperature'),
            weight=clinical_data.get('weight'),
            height=clinical_data.get('height'),
            bmi=clinical_data.get('bmi'),
            next_appointment=clinical_data.get('next_appointment')
        )

    def to_dict(self):
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            
            # Información del médico (inmutable)
            'doctor_name': self.doctor_name,
            'doctor_email': self.doctor_email,
            'doctor_role': self.doctor_role,
            'doctor_id_snapshot': self.doctor_id_snapshot,
            'doctor_license': self.doctor_license,
            'doctor_specialization': self.doctor_specialization,
            
            # Datos clínicos
            'visit_date': self.visit_date.isoformat() if self.visit_date else None,
            'reason_visit': self.reason_visit,
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
            
            # Información del paciente
            'patient_name': self.patient.full_name if self.patient else None
        }