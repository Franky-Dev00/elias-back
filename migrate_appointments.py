# migrate_appointments.py
from app import app
from models import db
from sqlalchemy import text

def migrate_appointments():
    with app.app_context():
        try:
            print("Creando tabla de citas...")
            
            # Crear tabla appointment
            migration_sql = text('''
            CREATE TABLE IF NOT EXISTS appointment (
                id SERIAL PRIMARY KEY,
                patient_id INTEGER NOT NULL REFERENCES patient(id),
                
                -- Información inmutable del médico
                doctor_name VARCHAR(120) NOT NULL,
                doctor_email VARCHAR(120) NOT NULL,
                doctor_role VARCHAR(50) NOT NULL,
                doctor_id_snapshot INTEGER,
                
                -- Información de la cita
                appointment_date TIMESTAMP NOT NULL,
                duration_minutes INTEGER DEFAULT 30,
                appointment_type VARCHAR(100) NOT NULL,
                reason TEXT NOT NULL,
                status VARCHAR(20) DEFAULT 'pendiente' NOT NULL,
                
                -- Información adicional
                observations TEXT,
                cancellation_reason TEXT,
                
                -- Usuario creador
                created_by_name VARCHAR(120) NOT NULL,
                created_by_role VARCHAR(50) NOT NULL,
                
                -- Auditoría
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
            );
            
            -- Índices para mejorar rendimiento
            CREATE INDEX IF NOT EXISTS idx_appointment_patient ON appointment(patient_id);
            CREATE INDEX IF NOT EXISTS idx_appointment_doctor ON appointment(doctor_id_snapshot);
            CREATE INDEX IF NOT EXISTS idx_appointment_date ON appointment(appointment_date);
            CREATE INDEX IF NOT EXISTS idx_appointment_status ON appointment(status);
            ''')
            
            db.session.execute(migration_sql)
            db.session.commit()
            
            print("Tabla de citas creada exitosamente")
            print("Índices creados para optimizar consultas")
            print("\nSistema de citas listo para usar")
            
        except Exception as e:
            print(f"Error durante la migración: {e}")
            db.session.rollback()
            raise

if __name__ == "__main__":
    migrate_appointments()