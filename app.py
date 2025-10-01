from flask import Flask                    # Importa la clase Flask para crear la aplicación web
from models.db import db                   # Importa la instancia de la base de datos SQLAlchemy
from routes.users import users_bp          # Importa el blueprint de rutas de usuarios
from routes.responsibles import responsibles_bp  # Importa el blueprint de rutas de responsables
from routes.tasks import tasks_bp          # Importa el blueprint de rutas de tareas
from dotenv import load_dotenv             # Importa la función para cargar variables de entorno desde un archivo .env
import os                                 # Importa el módulo os para acceder a variables de entorno
from routes.auth import auth_bp           # (Nuevo) Importa el modulo auth para autenticar usuarios
from flask_jwt_extended import JWTManager  #(nuevo) Importa la función JWT
from datetime import timedelta             # importar la funcion timedelta para que expire el token
from routes.patients import patients_bp     # Importa el blueprint de rutas de pacientes
from routes.clinicalrecords import clinical_records_bp # Importa el blueprint de rutas de registro clínico
from routes.dashboard import dashboard_bp   # Dashboard
from flask_cors import CORS                 # Añadido para habilitar CORS
from routes.appointments import appointments_bp  #

load_dotenv()                              # Carga variables de entorno desde el archivo .env

app = Flask(__name__)                     # Crea la instancia principal de la aplicación Flask

#app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL = os.getenv('DATABASE_URL')  # Configura la URL de la base de datos desde la variable de entorno
database_url = os.getenv('DATABASE_URL')
if not database_url:
    raise ValueError("DATABASE_URL no está configurada")
app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False  # Desactiva el seguimiento de modificaciones para mejorar el rendimiento

#app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "clave-super-secreta")

jwt_secret = os.getenv("JWT_SECRET_KEY")
if not jwt_secret:
    raise ValueError("JWT_SECRET_KEY no está configurada")

app.config["JWT_SECRET_KEY"] = jwt_secret
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=24)        # Token expira en 24 horas
app.config["JWT_TOKEN_LOCATION"] = ["headers"]                      # Donde buscar el token
app.config["JWT_HEADER_NAME"] = "Authorization"                     # Nombre del header
app.config["JWT_HEADER_TYPE"] = "Bearer"                            # Tipo de autenticación

# CORS
CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:3000", "http://44.199.207.193:3000"],
        "methods": ["GET", "POST", "PUT", "DELETE"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

app.register_blueprint(users_bp)          # Registra el blueprint de usuarios en la aplicación
app.register_blueprint(responsibles_bp)   # Registra el blueprint de responsables en la aplicación
app.register_blueprint(tasks_bp)          # Registra el blueprint de tareas en la aplicación
app.register_blueprint(auth_bp)           # (Nuevo) Registra el blueprint autenticación en la app
app.register_blueprint(patients_bp)       # 
app.register_blueprint(clinical_records_bp) #
app.register_blueprint(dashboard_bp)        #
app.register_blueprint(appointments_bp)     #

jwt = JWTManager(app)                     # inicializar JWT

db.init_app(app)                          # Inicializa la base de datos con la aplicación Flask

# Ruta de inicio
@app.route("/")
def home():
    try:
        return "Bienvenido a la API de Tareas con Flask"  # Devuelve un mensaje de bienvenida
    except Exception as e:
        return jsonify({"error": str(e)}), 500            # Si ocurre un error, devuelve el mensaje en formato JSON y código 500

with app.app_context():
    db.create_all()                       # Crea todas las tablas en la base de datos según los modelos definidos

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8083)  # Ejecuta la aplicación Flask en modo debug, accesible desde cualquier IP en el puerto 8083
