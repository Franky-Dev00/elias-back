from .db import db
from .user import User
from .task import Task
from .responsible import Responsible
from .patient import Patient
from .clinicalrecord import ClinicalRecord
from .appointment import Appointment

    # Lista de todos los modelos exportados
__all__ = ['db', 'User', 'Task', 'Responsible', 'Patient', 'ClinicalRecord', 'Appointment']