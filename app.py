from flask import Flask, render_template
import sqlite3
import os
from variables import Variables
from functions import list_to_str_html, import_db
app = Flask(__name__)


@app.route('/')
def hello_world():
    return render_template("index.html")


@app.route('/importardata')
def act1():
    x = import_db()
    if x:
        return render_template("index.html", title="Importar Data", content="No New Data")
    return render_template("index.html", title="Importar Data", content="Database Imported")


@app.route('/estudiantesactivos')
def act2():
    if not os.path.exists("database.db"):
        import_db()
    if Variables.estudiantes_activos is not None:
        return render_template("index.html", title="Estudiantes Activos", content=Variables.estudiantes_activos)
    else:
        conn = sqlite3.connect('database.db')
        conn.row_factory = lambda cursor, row: row[0]
        c = conn.cursor()
        student_id = c.execute("select estudiante from Inscripcioncurso where estado == 1").fetchall()
        users = []
        groups = []
        curso_id = []
        fecha_inscripcion = []
        fecha_vencimiento = []
        for i in student_id:
            users.append(c.execute("select usuario from Usuario where id == " + str(i)).fetchall())
            groups.append(c.execute("select groups from Usuario where id == " + str(i)).fetchall())
            curso_id.append(c.execute(" select curso from Inscripcioncurso where estudiante == " + str(i)).fetchall())
            fecha_inscripcion.append(c.execute(" select fecha_inscripcion from Inscripcioncurso where estudiante == " +
                                               str(i)).fetchall())
            fecha_vencimiento.append(c.execute(" select fecha_vencimiento from Inscripcioncurso where estudiante == " +
                                               str(i)).fetchall())
        curso_name = []
        es_gratis = []
        estado = []
        for x in curso_id:
            names = []
            for i in x:
                if i is not None:
                    names.append(c.execute("select nombre from Curso where id == " + str(i)).fetchall())
                    es_gratis.append(c.execute("select es_gratis from Curso where id == " + str(i)).fetchall())
                    estado.append(c.execute("select estado from Curso where id == " + str(i)).fetchall())
            curso_name.append(names)
        result = "<table class='center'><tr><th>Usuarios</th><th>Groups</th><th>Cursos</th></tr>"
        for (user, group, name) in zip(users, groups, curso_name):
            result += "<tr><td>" + user[0] + "</td>"
            if group is not None:
                conv = lambda it: it or 'NA'
                group = [conv(i) for i in group]
                result += "<td rowspan=>" + ' '.join(group) + "</td>"
            else:
                result += "<td>NA</td>"
            result += "<td>" + list_to_str_html(name, fecha_inscripcion, fecha_vencimiento, es_gratis, estado) + "</td>"
            result += "</tr>"
        result += "</table>"
        conn.close()
        Variables.estudiantes_activos = result
        return render_template("index.html", title="Estudiantes Activos", content=result)


@app.route('/analiticavideos')
def act3():
    if not os.path.exists("database.db"):
        import_db()
    if Variables.analitica_video is not None:
        return render_template("index.html", title="Analitica Video", content=Variables.analitica_video)
    else:
        conn = sqlite3.connect('database.db')
        conn.row_factory = lambda cursor, row: row[0]
        c = conn.cursor()
        inscripcion_id = c.execute("select inscripcion_curso from AnaliticaVideo").fetchall()
        estado_inscripcion = []
        curso_id = []
        curso_nombre = []
        for i in inscripcion_id:
            estado_inscripcion.append(c.execute("select estado from Inscripcioncurso where id =="+str(i)).fetchall())
            curso_id.append(c.execute("select curso from Inscripcioncurso where id ==" + str(i)).fetchall())
            curso_nombre.append(c.execute("select nombre from Curso where id =="+str(curso_id[-1][0])).fetchall())
        tema_reproduccion = c.execute("select tema_reproduccion from AnaliticaVideo").fetchall()
        estado_completado = c.execute("select estado_completado from AnaliticaVideo").fetchall()
        cantidad_reproduccion = c.execute("select cantidad_reproduccion from AnaliticaVideo").fetchall()
        nombre = []
        usiario_ids = []
        for i in inscripcion_id:
            usiario_ids.append(c.execute("select estudiante from Inscripcioncurso where id =="+str(i)).fetchall())
            nombre.append(c.execute("select usuario from Usuario where id =="+str(usiario_ids[-1][0])).fetchall())
        completos = 0
        percentage = []
        for(t, e, c) in zip(tema_reproduccion, estado_completado, cantidad_reproduccion):
            percentage.append(round(c/t*100, 2))
            if estado_completado:
                completos += 1
        result = "<table class='center'><tr><th>Estudiante id</th><th>Nombre</th><th>Curso id</th>" \
                 "<th>Curso nombre</th><th>progreso (%)</th></tr>"
        for (n, p, u, c, cn) in zip(nombre, percentage, usiario_ids, curso_id, curso_nombre):
            result += "<tr><td>" + str(u[0]) + "</td><td>" + n[0] + "</td><td>" + str(c[0]) + "</td><td>" +\
                      str(cn[0]) + "</td><td>" + str(p) + "</td>"
            result += "</tr>"
        result += "</table>"
        conn.close()
        Variables.analitica_video = result
        return render_template("index.html", title="Analitica Video", content=result)


if __name__ == '__main__':
    app.run()
