from models.db import db
from datetime import datetime

# Todo lo relacionado con Citas ->
class Appointment(db.Model):
    __tablename__ = 'appointment'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    
    # Información inmutable del médico (igual que en fichas clínicas)
    doctor_name = db.Column(db.String(120), nullable=False)
    doctor_email = db.Column(db.String(120), nullable=False)
    doctor_role = db.Column(db.String(50), nullable=False)
    doctor_id_snapshot = db.Column(db.Integer, nullable=True)
    
    # Información de la cita
    appointment_date = db.Column(db.DateTime, nullable=False)
    duration_minutes = db.Column(db.Integer, default=30)  # Duración en minutos
    appointment_type = db.Column(db.String(100), nullable=False)  # Control, consulta, emergencia, etc.
    reason = db.Column(db.Text, nullable=False)  # Motivo de la cita
    
    # Estado de la cita
    status = db.Column(db.String(20), default='pendiente', nullable=False)  # pendiente, confirmada, cancelada, completada
    
    # Información adicional
    observations = db.Column(db.Text)  # Observaciones adicionales
    cancellation_reason = db.Column(db.Text)  # Razón de cancelación si aplica
    
    # Usuario que creó/modificó la cita
    created_by_name = db.Column(db.String(120), nullable=False)
    created_by_role = db.Column(db.String(50), nullable=False)
    
    # Auditoría
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relación con paciente
    patient = db.relationship('Patient', backref='appointments')
    
    def __repr__(self):
        return f'<Appointment {self.id} - Patient {self.patient_id} - {self.appointment_date}>'

    @classmethod
    def create_with_users_info(cls, patient_id, doctor_user, creator_user, appointment_data):
        """
        Método para crear una cita capturando información inmutable de médico y creador
        """
        return cls(
            patient_id=patient_id,
            # Información del médico asignado
            doctor_name=doctor_user.full_name,
            doctor_email=doctor_user.mail,
            doctor_role=doctor_user.role,
            doctor_id_snapshot=doctor_user.id,
            # Información del creador
            created_by_name=creator_user.full_name,
            created_by_role=creator_user.role,
            # Datos de la cita
            appointment_date=appointment_data.get('appointment_date'),
            duration_minutes=appointment_data.get('duration_minutes', 30),
            appointment_type=appointment_data.get('appointment_type'),
            reason=appointment_data.get('reason'),
            status=appointment_data.get('status', 'pendiente'),
            observations=appointment_data.get('observations')
        )
    
    def is_conflict_with(self, other_appointment):
        """
        Verifica si esta cita tiene conflicto de horario con otra
        """
        if self.doctor_id_snapshot != other_appointment.doctor_id_snapshot:
            return False  # Diferentes médicos, no hay conflicto
        
        # Calcular fin de cada cita
        self_end = self.appointment_date + timedelta(minutes=self.duration_minutes)
        other_end = other_appointment.appointment_date + timedelta(minutes=other_appointment.duration_minutes)
        
        # Verificar si hay solapamiento
        return (self.appointment_date < other_end and self_end > other_appointment.appointment_date)
    
    def to_dict(self):
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'patient_name': self.patient.full_name if self.patient else None,
            
            # Información del médico
            'doctor_name': self.doctor_name,
            'doctor_email': self.doctor_email,
            'doctor_role': self.doctor_role,
            'doctor_id_snapshot': self.doctor_id_snapshot,
            
            # Información de la cita
            'appointment_date': self.appointment_date.isoformat() if self.appointment_date else None,
            'duration_minutes': self.duration_minutes,
            'appointment_type': self.appointment_type,
            'reason': self.reason,
            'status': self.status,
            'observations': self.observations,
            'cancellation_reason': self.cancellation_reason,
            
            # Información del creador
            'created_by_name': self.created_by_name,
            'created_by_role': self.created_by_role,
            
            # Auditoría
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

# Importar timedelta para cálculo de conflictos
from datetime import timedelta