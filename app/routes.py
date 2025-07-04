# app/routes.py
from flask import Blueprint, render_template, request, redirect, url_for
from app.models import db, Persona, Evaluacion, Asistencia, Certificado

mainRoutes = Blueprint('mainRoutes', __name__)

@mainRoutes.route('/')
def home():
    return render_template('home.html')


@mainRoutes.route('/personas')
def listarPersonas():
    personas = Persona.query.all()
    return render_template('personas/listarPersonas.html', personas=personas)


@mainRoutes.route('/personas/nueva', methods=['GET', 'POST'])
def crearPersona():
    if request.method == 'POST':
        nuevaPersona = Persona(
            nombres=request.form['nombres'],
            apellidos=request.form['apellidos'],
            cedula=request.form['cedula'],
            fecha_Nacimiento=request.form['fecha_Nacimiento'],
            telefono=request.form.get('telefono'),
            email=request.form.get('email'),
            direccion=request.form.get('direccion'),
            genero=request.form.get('genero'),
            estado_Civil=request.form.get('estado_Civil'),
            activo=True
        )
        db.session.add(nuevaPersona)
        db.session.commit()
        return redirect(url_for('mainRoutes.listarPersonas'))
    return render_template('personas/crearPersona.html')
@mainRoutes.route('/personas/editar/<int:id>', methods=['GET', 'POST'])
def editarPersona(id):
    persona = Persona.query.get_or_404(id)

    if request.method == 'POST':
        persona.nombres = request.form['nombres']
        persona.apellidos = request.form['apellidos']
        persona.cedula = request.form['cedula']
        persona.fecha_Nacimiento = request.form['fecha_Nacimiento']
        persona.telefono = request.form.get('telefono')
        persona.email = request.form.get('email')
        persona.direccion = request.form.get('direccion')
        persona.genero = request.form.get('genero')
        persona.estado_Civil = request.form.get('estado_Civil')

        db.session.commit()
        return redirect(url_for('mainRoutes.listarPersonas'))

    return render_template('personas/editarPersona.html', persona=persona)


@mainRoutes.route('/personas/eliminar/<int:id>', methods=['POST'])
def eliminarPersona(id):
    persona = Persona.query.get_or_404(id)
    db.session.delete(persona)
    db.session.commit()
    return redirect(url_for('mainRoutes.listarPersonas'))


from app.models import Catequizando, Parroquia, Nivel

@mainRoutes.route('/catequizandos')
def listarCatequizandos():
    catequizandos = Catequizando.query.all()
    return render_template('catequizandos/listarCatequizandos.html', catequizandos=catequizandos)


@mainRoutes.route('/catequizandos/nuevo', methods=['GET', 'POST'])
def crearCatequizando():
    personas = Persona.query.all()
    parroquias = Parroquia.query.all()
    niveles = Nivel.query.all()

    if request.method == 'POST':
        nuevoCatequizando = Catequizando(
            persona_Id=request.form['persona_Id'],
            parroquia_Id=request.form['parroquia_Id'],
            nivel_Actual=request.form.get('nivel_Actual'),
            fecha_Ingreso=request.form['fecha_Ingreso'],
            estado='Activo'
        )
        db.session.add(nuevoCatequizando)
        db.session.commit()
        return redirect(url_for('mainRoutes.listarCatequizandos'))

    return render_template(
        'catequizandos/crearCatequizando.html',
        personas=personas,
        parroquias=parroquias,
        niveles=niveles
    )
@mainRoutes.route('/catequizandos/editar/<int:id>', methods=['GET', 'POST'])
def editarCatequizando(id):
    catequizando = Catequizando.query.get_or_404(id)
    personas = Persona.query.all()
    parroquias = Parroquia.query.all()
    niveles = Nivel.query.all()

    if request.method == 'POST':
        catequizando.persona_Id = request.form['persona_Id']
        catequizando.parroquia_Id = request.form['parroquia_Id']
        catequizando.nivel_Actual = request.form.get('nivel_Actual') or None
        catequizando.fecha_Ingreso = request.form['fecha_Ingreso']
        catequizando.fecha_Salida = request.form.get('fecha_Salida')
        catequizando.motivo_Salida = request.form.get('motivo_Salida')
        catequizando.estado = request.form['estado']
        db.session.commit()
        return redirect(url_for('mainRoutes.listarCatequizandos'))

    return render_template(
        'catequizandos/editarCatequizando.html',
        catequizando=catequizando,
        personas=personas,
        parroquias=parroquias,
        niveles=niveles
    )


@mainRoutes.route('/catequizandos/eliminar/<int:id>', methods=['POST'])
def eliminarCatequizando(id):
    catequizando = Catequizando.query.get_or_404(id)
    db.session.delete(catequizando)
    db.session.commit()
    return redirect(url_for('mainRoutes.listarCatequizandos'))



@mainRoutes.route('/parroquias')
def listarParroquias():
    parroquias = Parroquia.query.all()
    return render_template('parroquias/listarParroquias.html', parroquias=parroquias)


@mainRoutes.route('/parroquias/nueva', methods=['GET', 'POST'])
def crearParroquia():
    if request.method == 'POST':
        nuevaParroquia = Parroquia(
            nombre=request.form['nombre'],
            direccion=request.form['direccion'],
            telefono=request.form.get('telefono'),
            es_Principal=True if request.form.get('es_Principal') == 'on' else False,
            fecha_Fundacion=request.form.get('fecha_Fundacion'),
            historia=request.form.get('historia'),
            horarios_Atencion=request.form.get('horarios_Atencion'),
            sitio_Web=request.form.get('sitio_Web'),
            email=request.form.get('email')
        )
        db.session.add(nuevaParroquia)
        db.session.commit()
        return redirect(url_for('mainRoutes.listarParroquias'))

    return render_template('parroquias/crearParroquia.html')
@mainRoutes.route('/parroquias/editar/<int:id>', methods=['GET', 'POST'])
def editarParroquia(id):
    parroquia = Parroquia.query.get_or_404(id)

    if request.method == 'POST':
        parroquia.nombre = request.form['nombre']
        parroquia.direccion = request.form['direccion']
        parroquia.telefono = request.form.get('telefono')
        parroquia.es_Principal = True if request.form.get('es_Principal') == 'on' else False
        parroquia.fecha_Fundacion = request.form.get('fecha_Fundacion')
        parroquia.historia = request.form.get('historia')
        parroquia.horarios_Atencion = request.form.get('horarios_Atencion')
        parroquia.sitioWeb = request.form.get('sitioWeb')
        parroquia.email = request.form.get('email')

        db.session.commit()
        return redirect(url_for('mainRoutes.listarParroquias'))

    return render_template('parroquias/editarParroquia.html', parroquia=parroquia)


@mainRoutes.route('/parroquias/eliminar/<int:id>', methods=['POST'])
def eliminarParroquia(id):
    parroquia = Parroquia.query.get_or_404(id)
    db.session.delete(parroquia)
    db.session.commit()
    return redirect(url_for('mainRoutes.listarParroquias'))
from app.models import Evaluacion

@mainRoutes.route('/evaluaciones')
def listarEvaluaciones():
    evaluaciones = Evaluacion.query.all()
    return render_template('evaluaciones/listarEvaluaciones.html', evaluaciones=evaluaciones)


@mainRoutes.route('/evaluaciones/nueva', methods=['GET', 'POST'])
def crearEvaluacion():
    catequizandos = Catequizando.query.all()
    niveles = Nivel.query.all()

    if request.method == 'POST':
        nuevaEvaluacion = Evaluacion(
            catequizando_id=request.form['catequizando_id'],
            nivel_id=request.form['nivel_id'],
            fecha=request.form['fecha'],
            nota=request.form['nota'],
            observaciones=request.form.get('observaciones')
        )
        db.session.add(nuevaEvaluacion)
        db.session.commit()
        return redirect(url_for('mainRoutes.listarEvaluaciones'))

    return render_template('evaluaciones/crearEvaluacion.html', catequizandos=catequizandos, niveles=niveles)

from app.models import Asistencia

@mainRoutes.route('/asistencias')
def listarAsistencias():
    asistencias = Asistencia.query.order_by(Asistencia.fecha.desc()).all()
    return render_template('asistencias/listarAsistencias.html', asistencias=asistencias)


@mainRoutes.route('/asistencias/nueva', methods=['GET', 'POST'])
def registrarAsistencia():
    catequizandos = Catequizando.query.all()

    if request.method == 'POST':
        nuevaAsistencia = Asistencia(
            catequizando_id=request.form['catequizando_id'],
            fecha=request.form['fecha'],
            estado=True if request.form.get('estado') == 'on' else False
        )
        db.session.add(nuevaAsistencia)
        db.session.commit()
        return redirect(url_for('mainRoutes.listarAsistencias'))

    return render_template('asistencias/registrarAsistencia.html', catequizandos=catequizandos)

from datetime import date
from sqlalchemy import and_

@mainRoutes.route('/certificados')
def listarCertificados():
    certificados = Certificado.query.all()
    return render_template('certificados/listarCertificados.html', certificados=certificados)


@mainRoutes.route('/certificados/generar', methods=['GET', 'POST'])
def generarCertificado():
    catequizandos = Catequizando.query.all()
    niveles = Nivel.query.all()

    if request.method == 'POST':
        catequizando_id = request.form['catequizando_id']
        nivel_id = request.form['nivel_id']

        evaluacion = Evaluacion.query.filter_by(
            catequizando_id=catequizando_id,
            nivel_id=nivel_id
        ).order_by(Evaluacion.nota.desc()).first()

        if evaluacion and evaluacion.nota >= 70:
            nuevoCertificado = Certificado(
                catequizando_id=catequizando_id,
                nivel_id=nivel_id,
                fecha_Emision=date.today(),
                observacion='Aprobado con éxito'
            )
            db.session.add(nuevoCertificado)
            db.session.commit()
            return redirect(url_for('mainRoutes.listarCertificados'))
        else:
            return "El catequizando no tiene evaluación aprobada para este nivel."

    return render_template('certificados/generarCertificado.html', catequizandos=catequizandos, niveles=niveles)

from sqlalchemy.sql import func

@mainRoutes.route('/reportes')
def reportesGenerales():
    total_Catequizandos = db.session.query(func.count(Catequizando.id)).scalar()

    catequizandosPorNivel = db.session.query(
        Nivel.nombre,
        func.count(Catequizando.id)
    ).join(Catequizando, Catequizando.nivelActual == Nivel.id)\
     .group_by(Nivel.nombre).all()

    promedio_Evaluaciones = db.session.query(
        func.avg(Evaluacion.nota)
    ).scalar()

    certificados_Emitidos = db.session.query(func.count(Certificado.id)).scalar()

    asistencias = db.session.query(func.count(Asistencia.id)).scalar()
    asistenciasSi = db.session.query(func.count(Asistencia.id))\
        .filter(Asistencia.estado == True).scalar()
    porcentaje_Asistencia = (asistenciasSi / asistencias * 100) if asistencias else 0

    return render_template(
        'reportes/reportesGenerales.html',
        total_Catequizandos=total_Catequizandos,
        catequizandosPorNivel=catequizandosPorNivel,
        promedio_Evaluaciones=round(promedio_Evaluaciones, 2) if promedio_Evaluaciones else 0,
        certificados_Emitidos=certificados_Emitidos,
        porcentaje_Asistencia=round(porcentaje_Asistencia, 2)
    )






