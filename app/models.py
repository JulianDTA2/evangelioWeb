# app/models.py
from app import db

class Persona(db.Model):
    __tablename__ = 'Persona'
    __table_args__ = {'schema': 'Administracion'}

    id = db.Column(db.Integer, primary_key=True)
    nombres = db.Column(db.String(100), nullable=False)
    apellidos = db.Column(db.String(100), nullable=False)
    cedula = db.Column(db.String(10), unique=True, nullable=False)
    fecha_Nacimiento = db.Column(db.Date, nullable=False)
    telefono = db.Column(db.String(15))
    email = db.Column(db.String(100))
    direccion = db.Column(db.String(150))
    genero = db.Column(db.String(1))
    estado_Civil = db.Column(db.String(20))
    fecha_Registro = db.Column(db.DateTime)
    activo = db.Column(db.Boolean)

    def __repr__(self):
        return f'<Persona {self.nombres} {self.apellidos}>'


class Parroquia(db.Model):
    __tablename__ = 'Parroquia'
    __table_args__ = {'schema': 'Catequesis'}

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    direccion = db.Column(db.String(150), nullable=False)
    telefono = db.Column(db.String(15))
    es_principal = db.Column('es_principal', db.Boolean, default=False)
    fecha_Fundacion = db.Column(db.Date)
    historia = db.Column(db.Text)
    horarios_Atencion = db.Column(db.String(255))
    sitio_Web = db.Column(db.String(100))
    email = db.Column(db.String(100))


class Nivel(db.Model):
    __tablename__ = 'Nivel'
    __table_args__ = {'schema': 'Catequesis'}

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    descripcion = db.Column(db.String(200))
    duracion_semanas = db.Column('duracion_semanas', db.Integer, nullable=False)
    edad_minima = db.Column(db.Integer)
    edad_maxima = db.Column(db.Integer)
    requisitos = db.Column(db.Text)


class Catequizando(db.Model):
    __tablename__ = 'Catequizando'
    __table_args__ = {'schema': 'Catequesis'}

    id = db.Column(db.Integer, primary_key=True)
    persona_Id = db.Column(db.Integer, db.ForeignKey('Administracion.Persona.id'), nullable=False)
    parroquia_Id = db.Column(db.Integer, db.ForeignKey('Catequesis.Parroquia.id'), nullable=False)
    nivel_Actual = db.Column(db.Integer, db.ForeignKey('Catequesis.Nivel.id'))
    fecha_Ingreso = db.Column(db.Date, nullable=False)
    fecha_Salida = db.Column(db.Date)
    motivo_Salida = db.Column(db.String(100))
    estado = db.Column(db.String(20))

    persona = db.relationship('Persona')
    parroquia = db.relationship('Parroquia')
    nivel = db.relationship('Nivel')


    def __repr__(self):
        return f'<Catequizando ID {self.id}>'
    
class Evaluacion(db.Model):
    __tablename__  = 'Evaluacion'
    __table_args__ = {
        'schema': 'Catequesis',
        'implicit_returning': False     # ← clave: desactiva OUTPUT inserted.*
    }

    id              = db.Column(db.Integer, primary_key=True, autoincrement=True)
    catequizando_id = db.Column(db.Integer, db.ForeignKey('Catequesis.Catequizando.id'))
    nivel_id        = db.Column(db.Integer, db.ForeignKey('Catequesis.Nivel.id'))
    nota            = db.Column(db.Numeric(4, 2))              # 0 – 10
    fecha           = db.Column(db.Date)                       # ≤ GETDATE()
    aprobado        = db.Column(db.Boolean, nullable=False)
    observaciones   = db.Column(db.String(255))

    catequizando = db.relationship('Catequizando')
    nivel        = db.relationship('Nivel')
    
class Grupo(db.Model):
    __tablename__ = 'Grupo'
    __table_args__ = {'schema': 'Catequesis'}

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    nivel_id = db.Column(db.Integer, db.ForeignKey('Catequesis.Nivel.id'), nullable=False)
    catequista_principal_id = db.Column(db.Integer, db.ForeignKey('Catequesis.Catequista.id'), nullable=False)
    joven_apoyo_id = db.Column(db.Integer, db.ForeignKey('Catequesis.Catequista.id'))
    horario = db.Column(db.String(50), nullable=False)
    lugar = db.Column(db.String(100))
    capacidad = db.Column(db.Integer)
    estado = db.Column(db.String(20), default='Activo')
    fecha_inicio = db.Column(db.Date, nullable=False)
    fecha_fin = db.Column(db.Date)

class Asistencia(db.Model):
    __tablename__  = 'Asistencia'
    __table_args__ = {'schema': 'Catequesis', 'implicit_returning': False}

    id              = db.Column(db.Integer, primary_key=True, autoincrement=True)
    grupo_id        = db.Column(db.Integer, db.ForeignKey('Catequesis.Grupo.id'), nullable=False)
    catequizando_id = db.Column(db.Integer, db.ForeignKey('Catequesis.Catequizando.id'), nullable=False)
    fecha           = db.Column(db.Date, nullable=False)
    estado          = db.Column(db.String(1), nullable=False)       # 'P', 'A', 'J'
    observaciones   = db.Column(db.String(255))
    registrado_por  = db.Column(db.Integer)

    grupo = db.relationship("Grupo")
    catequizando = db.relationship("Catequizando")


class Certificado(db.Model):
    __tablename__ = 'Certificado'
    __table_args__ = {'schema': 'Catequesis'}

    id = db.Column(db.Integer, primary_key=True)
    catequizando_id = db.Column(db.Integer, db.ForeignKey('Catequesis.Catequizando.id'), nullable=False)
    nivel_id = db.Column(db.Integer, db.ForeignKey('Catequesis.Nivel.id'), nullable=False)
    fecha_emision = db.Column('fecha_emision', db.Date, nullable=False)
    fecha_entrega = db.Column(db.Date)
    recibido_por = db.Column(db.String(100))
    estado = db.Column(db.String(20), nullable=False)
    codigo_verificacion = db.Column(db.String(50), unique=True)

    catequizando = db.relationship('Catequizando')
    nivel = db.relationship('Nivel')

from sqlalchemy import Column, Integer
from . import db  # o desde donde importes tu instancia SQLAlchemy

class Catequista(db.Model):
    __tablename__   = 'Catequista'
    __table_args__  = {'schema': 'Catequesis'}
    
    id = Column(Integer, primary_key=True, autoincrement=True)

