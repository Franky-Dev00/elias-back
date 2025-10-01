# migrate_simple.py
from app import app
from models import db
from sqlalchemy import text

def migrate_database():
    with app.app_context():
        try:
            print("Iniciando migración a fichas clínicas inmutables...")
            
            # Paso 1: Agregar nuevas columnas
            print("Agregando columnas para información inmutable del médico...")
            
            migration_sql = text('''
            ALTER TABLE clinical_record 
            ADD COLUMN IF NOT EXISTS doctor_name VARCHAR(120),
            ADD COLUMN IF NOT EXISTS doctor_email VARCHAR(120),
            ADD COLUMN IF NOT EXISTS doctor_role VARCHAR(50),
            ADD COLUMN IF NOT EXISTS doctor_id_snapshot INTEGER,
            ADD COLUMN IF NOT EXISTS doctor_license VARCHAR(50),
            ADD COLUMN IF NOT EXISTS doctor_specialization VARCHAR(100),
            ADD COLUMN IF NOT EXISTS reason_visit TEXT;
            
            ALTER TABLE clinical_record ALTER COLUMN doctor_id DROP NOT NULL;
            ''')
            
            db.session.execute(migration_sql)
            db.session.commit()
            print("Columnas agregadas exitosamente")
            
            # Paso 2: Migrar fichas existentes (si las hay)
            print("Migrando fichas existentes...")
            
            # Obtener fichas existentes
            existing_records_sql = text('''
                SELECT cr.id, cr.doctor_id, u.full_name, u.mail, u.role
                FROM clinical_record cr
                LEFT JOIN "user" u ON cr.doctor_id = u.id
                WHERE cr.doctor_name IS NULL;
            ''')
            
            existing_records = db.session.execute(existing_records_sql).fetchall()
            
            for record in existing_records:
                record_id, doctor_id, doctor_name, doctor_email, doctor_role = record
                
                # Si el médico existe, usar sus datos; si no, datos genéricos
                if doctor_name:
                    update_sql = text('''
                        UPDATE clinical_record 
                        SET doctor_name = :doctor_name,
                            doctor_email = :doctor_email,
                            doctor_role = :doctor_role,
                            doctor_id_snapshot = :doctor_id,
                            reason_visit = COALESCE(reason_visit, 'Consulta médica')
                        WHERE id = :record_id;
                    ''')
                    db.session.execute(update_sql, {
                        'doctor_name': doctor_name,
                        'doctor_email': doctor_email,
                        'doctor_role': doctor_role,
                        'doctor_id': doctor_id,
                        'record_id': record_id
                    })
                else:
                    # Médico eliminado - preservar con datos genéricos
                    update_sql = text('''
                        UPDATE clinical_record 
                        SET doctor_name = 'Médico (registro histórico)',
                            doctor_email = 'historico@clinica.com',
                            doctor_role = 'medico',
                            doctor_id_snapshot = :doctor_id,
                            reason_visit = COALESCE(reason_visit, 'Consulta médica')
                        WHERE id = :record_id;
                    ''')
                    db.session.execute(update_sql, {
                        'doctor_id': doctor_id,
                        'record_id': record_id
                    })
                
                print(f"Migrada ficha ID {record_id}")
            
            db.session.commit()
            
            # Paso 3: Hacer campos obligatorios
            print("Estableciendo campos obligatorios...")
            
            constraints_sql = text('''
                ALTER TABLE clinical_record 
                ALTER COLUMN doctor_name SET NOT NULL,
                ALTER COLUMN doctor_email SET NOT NULL,
                ALTER COLUMN doctor_role SET NOT NULL,
                ALTER COLUMN reason_visit SET NOT NULL;
            ''')
            
            db.session.execute(constraints_sql)
            db.session.commit()
            
            print("Migración completada exitosamente!")
            print("Ahora las fichas clínicas son completamente autónomas.")
            print("Los médicos pueden ser eliminados sin afectar las fichas.")
            
        except Exception as e:
            print(f"Error durante la migración: {e}")
            db.session.rollback()
            raise

if __name__ == "__main__":
    migrate_database()