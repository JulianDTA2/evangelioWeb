# app/routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models import db, Persona, Evaluacion, Asistencia, Certificado, Grupo, Nivel, Catequizando, Catequista
from sqlalchemy.sql import func
from datetime import date    

mainRoutes = Blueprint('mainRoutes', __name__)

@mainRoutes.route('/')
def home():
    return render_template('home.html')

@mainRoutes.route('/niveles')
def listarNiveles():
    niveles = Nivel.query.order_by(Nivel.id).all()
    return render_template('niveles/listarNiveles.html', niveles=niveles)


@mainRoutes.route('/niveles/nuevo', methods=['GET', 'POST'])
def crearNivel():
    if request.method == 'POST':
        nuevo = Nivel(
            nombre           = request.form['nombre'],
            descripcion      = request.form.get('descripcion'),
            duracion_semanas = request.form['duracion_semanas'],
            edad_minima      = request.form.get('edad_minima') or None,
            edad_maxima      = request.form.get('edad_maxima') or None,
            requisitos       = request.form.get('requisitos')
        )
        db.session.add(nuevo)
        db.session.commit()
        return redirect(url_for('mainRoutes.listarNiveles'))

    return render_template('niveles/crearNivel.html')


@mainRoutes.route('/niveles/editar/<int:id>', methods=['GET', 'POST'])
def editarNivel(id):
    nivel = Nivel.query.get_or_404(id)
    if request.method == 'POST':
        nivel.nombre           = request.form['nombre']
        nivel.descripcion      = request.form.get('descripcion')
        nivel.duracion_semanas = request.form['duracion_semanas']
        nivel.edad_minima      = request.form.get('edad_minima') or None
        nivel.edad_maxima      = request.form.get('edad_maxima') or None
        nivel.requisitos       = request.form.get('requisitos')
        db.session.commit()
        return redirect(url_for('mainRoutes.listarNiveles'))

    return render_template('niveles/editarNivel.html', nivel=nivel)


from sqlalchemy.exc import IntegrityError

@mainRoutes.route('/niveles/eliminar/<int:id>', methods=['POST'])
def eliminarNivel(id):
    nivel = Nivel.query.get_or_404(id)

    try:
        # 1) eliminar certificados que referencian este nivel
        Certificado.query.filter_by(nivel_id=id).delete(synchronize_session=False)

        # 2) eliminar evaluaciones que referencian este nivel
        Evaluacion.query.filter_by(nivel_id=id).delete(synchronize_session=False)

        # 3) (si usas Grupos ligados al nivel)
        Grupo.query.filter_by(nivel_id=id).delete(synchronize_session=False)

        # 4) poner a NULL el nivel_actual de los catequizandos
        Catequizando.query.filter_by(nivel_Actual=id)\
            .update({Catequizando.nivel_Actual: None},
                    synchronize_session=False)

        # 5) ahora sí, borrar el nivel
        db.session.delete(nivel)
        db.session.commit()
        flash('Nivel eliminado correctamente', 'success')

    except IntegrityError as e:          # cualquier FK pendiente
        db.session.rollback()
        flash(f'No se pudo eliminar: {e.orig}', 'danger')

    return redirect(url_for('mainRoutes.listarNiveles'))


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

    try:
        # ── 1) catequizandos vinculados a la persona ─────────────────
        for c in Catequizando.query.filter_by(persona_Id=id).all():

            # a) asistencias → grupos                              
            Asistencia.query.filter_by(catequizando_id=c.id)\
                            .delete(synchronize_session=False)

            # b) evaluaciones → certificados (los certificados cuelgan del nivel)     
            Certificado.query.filter_by(catequizando_id=c.id)\
                             .delete(synchronize_session=False)
            Evaluacion.query.filter_by(catequizando_id=c.id)\
                            .delete(synchronize_session=False)

            # c) cambios, excepciones, etc. (si los usas)
            CambioParroquia.query.filter_by(catequizando_id=c.id)\
                                 .delete(synchronize_session=False)
            Excepcion.query.filter_by(catequizando_id=c.id)\
                           .delete(synchronize_session=False)

            # por último el catequizando
            db.session.delete(c)
            
        # ── 3) ya podemos borrar la persona ─────────────────────────
        db.session.delete(persona)
        db.session.commit()
        flash('Persona eliminada correctamente', 'success')

    except IntegrityError as e:
        db.session.rollback()
        flash(f'No se pudo eliminar: {e.orig}', 'danger')

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

    if request.method == 'POST':
        # campos siempre presentes
        catequizando.persona_Id    = request.form['persona_Id']
        catequizando.parroquia_Id  = request.form['parroquia_Id']
        catequizando.nivel_Actual  = request.form.get('nivel_Actual') or None
        catequizando.fecha_Ingreso = request.form['fecha_Ingreso']

        # convertir vacíos a None
        fecha_salida = request.form.get('fecha_Salida') or None
        motivo       = request.form.get('motivo_Salida') or None

        catequizando.fecha_Salida  = fecha_salida
        catequizando.motivo_Salida = motivo
        catequizando.estado        = request.form['estado']

        db.session.commit()
        return redirect(url_for('mainRoutes.listarCatequizandos'))

    # GET → renderizar formulario
    personas   = Persona.query.all()
    parroquias = Parroquia.query.all()
    niveles    = Nivel.query.all()
    return render_template('catequizandos/editarCatequizando.html',
                           catequizando=catequizando,
                           personas=personas,
                           parroquias=parroquias,
                           niveles=niveles)



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
            es_principal=True if request.form.get('es_principal') == 'on' else False,
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
        parroquia.es_principal = True if request.form.get('es_principal') == 'on' else False
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

@mainRoutes.route('/crear-evaluacion', methods=['GET', 'POST'])
def crearEvaluacion():
    from datetime import date

    if request.method == 'POST':
        try:
            catequizando_id = request.form['catequizando_id']
            nivel_id        = request.form['nivel_id']

            # ---------- validación de NOTA ----------
            nota_str = request.form['nota']
            if not nota_str or not nota_str.isdigit():
                flash('La nota debe ser un número entre 0 y 10')
                return redirect(url_for('mainRoutes.crearEvaluacion'))
            nota = int(nota_str)
            if nota < 0 or nota > 10:
                flash('La nota debe estar entre 0 y 10')
                return redirect(url_for('mainRoutes.crearEvaluacion'))

            # ---------- validación de FECHA ----------
            fecha_str = request.form['fecha']
            if not fecha_str:
                flash('La fecha es obligatoria')
                return redirect(url_for('mainRoutes.crearEvaluacion'))
            fecha = date.fromisoformat(fecha_str)
            if fecha > date.today():
                flash('La fecha no puede ser futura')
                return redirect(url_for('mainRoutes.crearEvaluacion'))

            observaciones = request.form.get('observaciones', '')

            aprobado = nota >= 7   #  o la regla que uses

            nueva_eval = Evaluacion(
                catequizando_id=catequizando_id,
                nivel_id       =nivel_id,
                nota           =nota,
                fecha          =fecha,
                aprobado       =aprobado,
                observaciones  =observaciones
            )

            db.session.add(nueva_eval)
            db.session.commit()
            flash('Evaluación guardada correctamente')
            return redirect(url_for('mainRoutes.listarEvaluaciones'))

        except Exception as e:
            db.session.rollback()
            flash(f'Ocurrió un error al guardar la evaluación: {e}')
            return redirect(url_for('mainRoutes.crearEvaluacion'))

    # GET
    catequizandos = Catequizando.query.all()
    niveles       = Nivel.query.all()
    return render_template('evaluaciones/crearEvaluacion.html',
                           catequizandos=catequizandos,
                           niveles=niveles)


from app.models import Asistencia

@mainRoutes.route('/asistencias')
def listarAsistencias():
    asistencias = Asistencia.query.order_by(Asistencia.fecha.desc()).all()
    return render_template('asistencias/listarAsistencias.html', asistencias=asistencias)

def _get_dummy_catequista() -> "Catequista":
    dummy_cedula = "9999999999"

    per = (
        Persona.query.filter_by(cedula=dummy_cedula).first()
        or Persona(
            nombres="(Dummy)",
            apellidos="(Catequista)",
            cedula=dummy_cedula,
            fecha_Nacimiento=date(1990, 1, 1),
            activo=0,
        )
    )

    cat = (
        Catequista.query.filter_by(persona_id=per.id).first()
        if per.id
        else None
    )

    if not per.id:
        db.session.add(per)
        db.session.flush()  # ya tenemos per.id

    if not cat:
        cat = Catequista(persona_id=per.id, parroquia_id=1, fecha_inicio=date.today())
        db.session.add(cat)
        db.session.flush()

    return cat

@mainRoutes.route('/asistencias/nueva', methods=['GET', 'POST'])
def registrarAsistencia():
    niveles = Nivel.query.order_by(Nivel.nombre).all()
    catequizandos = Catequizando.query.order_by(Catequizando.id).all()

    if request.method == 'POST':
        nivel_id = request.form['nivel_id']
        catequizando_id = request.form['catequizando_id']
        estado = request.form['estado']                 # P  A  J
        fecha = request.form.get('fecha') or date.today()
        observaciones = request.form.get('observaciones')

        grupo = Grupo.query.filter_by(nivel_id=nivel_id).first()
        if not grupo:
            flash('No existe grupo registrado para ese nivel')
            return redirect(url_for('mainRoutes.registrarAsistencia'))

        cateq = Catequizando.query.get(catequizando_id)
        if not cateq or str(cateq.nivel_Actual) != str(nivel_id):
            flash('El catequizando no pertenece a ese nivel')
            return redirect(url_for('mainRoutes.registrarAsistencia'))

        asistencia = Asistencia(
            grupo_id=grupo.id,
            catequizando_id=catequizando_id,
            fecha=fecha,
            estado=estado,
            observaciones=observaciones,
            registrado_por=None
        )
        db.session.add(asistencia)
        db.session.commit()
        flash('Asistencia registrada correctamente')
        return redirect(url_for('mainRoutes.listarAsistencias'))

    return render_template(
        'asistencias/registrarAsistencia.html',
        niveles=niveles,
        catequizandos=catequizandos
    )

from datetime import date
from sqlalchemy import and_

@mainRoutes.route('/certificados')
def listarCertificados():
    certificados = Certificado.query.all()
    return render_template('certificados/listarCertificados.html', certificados=certificados)

@mainRoutes.route('/certificados/generar', methods=['GET', 'POST'])
def generarCertificado():
    catequizandos = Catequizando.query.all()
    niveles       = Nivel.query.all()

    if request.method == 'POST':
        catequizando_id = request.form['catequizando_id']
        nivel_id        = request.form['nivel_id']

        # ― buscar la evaluación aprobada (nota >= 7, ajusta si tu regla difiere)
        evaluacion = (Evaluacion.query
                      .filter_by(catequizando_id=catequizando_id,
                                 nivel_id=nivel_id,
                                 aprobado=True)
                      .order_by(Evaluacion.nota.desc())
                      .first())

        if not evaluacion:
            flash('El catequizando no tiene evaluación aprobada para este nivel.')
            return redirect(url_for('mainRoutes.generarCertificado'))

        # ― comprobar si YA existe un certificado para evitar duplicados
        existe = Certificado.query.filter_by(
            catequizando_id=catequizando_id,
            nivel_id=nivel_id
        ).first()
        if existe:
            flash('Ya existe un certificado para este nivel.')
            return redirect(url_for('mainRoutes.listarCertificados'))

        nuevoCertificado = Certificado(
            catequizando_id = catequizando_id,
            nivel_id        = nivel_id,
            fecha_Emision   = evaluacion.fecha,   # ← misma fecha de la evaluación aprobada
            observacion     = None                # ← ya no usaremos observación
        )

        db.session.add(nuevoCertificado)
        db.session.commit()
        flash('Certificado emitido correctamente')
        return redirect(url_for('mainRoutes.listarCertificados'))

    # GET
    return render_template('certificados/generarCertificado.html',
                           catequizandos=catequizandos,
                           niveles=niveles)
from sqlalchemy import func

@mainRoutes.route('/reportes')
def reportesGenerales():
    total_catequizandos = db.session.query(func.count(Catequizando.id)).scalar()

    # catequizandos por nivel -------------------------
    catequizandosPorNivel = (
        db.session.query(
            Nivel.nombre,
            func.count(Catequizando.id)
        )
        .outerjoin(Catequizando, Catequizando.nivel_Actual == Nivel.id)
        .group_by(Nivel.nombre)
        .all()
    )

    # promedio de notas -------------------------------
    promedio_Evaluaciones = db.session.query(func.avg(Evaluacion.nota)).scalar() or 0

    # certificados emitidos ---------------------------
    certificados_Emitidos = db.session.query(func.count(Certificado.id)).scalar()

    # asistencias -------------------------------------
    total_asistencias = db.session.query(func.count(Asistencia.id)).scalar()

    presentes = (
        db.session.query(func.count(Asistencia.id))
        .filter(Asistencia.estado == 'P')      # ← aquí va 'P'
        .scalar()
    )

    porcentaje_asistencia = (
        (presentes / total_asistencias * 100) if total_asistencias else 0
    )

    return render_template(
        'reportes/reportesGenerales.html',
        total_Catequizandos = total_catequizandos,
        catequizandosPorNivel = catequizandosPorNivel,
        promedio_Evaluaciones = round(promedio_Evaluaciones, 2),
        certificados_Emitidos = certificados_Emitidos,
        porcentaje_Asistencia = round(porcentaje_asistencia, 2)
    )
