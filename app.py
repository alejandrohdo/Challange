from flask import Flask, render_template
import sqlite3
import pandas as pd
import os
import re
from variables import Variables
app = Flask(__name__)


@app.route('/')
def hello_world():
    return render_template("index.html")


@app.route('/importardata')
def act1():
    tables = os.listdir("Data/")
    regex = re.compile('[^a-zA-Z]')
    con = sqlite3.connect("database.db")
    for table in tables:
        name = table.split('.')[0]
        name = regex.sub('', name)
        df = pd.read_excel('Data/{0}'.format(table), sheet_name="Tablib Dataset")
        df.to_sql(name, con, index=False, if_exists="replace")
    con.commit()
    con.close()
    Variables.estudiantes_activos = None
    Variables.analitica_video = None
    return render_template("index.html", title="Importar Data", content="Database Imported")


@app.route('/estudiantesactivos')
def act2():
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


def list_to_str_html(name, inscripcion, vencimiento, gratis, eastado):
    html_str = ""
    itr = 0
    for (n, i, v) in zip(name, inscripcion, vencimiento):
        html_str += str(n[0]) + "<br>"
        if gratis[itr][0] == 0:
            html_str += "Gratis: No"
        else:
            html_str += "Gratis: Si"
        html_str += ", "
        if eastado[itr][0] == 0:
            html_str += "Estado: Desactivado"
        else:
            html_str += "Estado: Activo"
        itr += 1
        html_str += "<br> Fecha de Inscripcion: " + str(i[0]) + ", Fecha de Vencimiento: " + str(v[0])
        html_str += "<br>"
        if n is not name[-1]:
            html_str += "<br>"
    return html_str


@app.route('/analiticavideos')
def act3():
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
        result = "<table class='center'><tr><th>Estudiante id</th><th>Nombre</th><th>Curso id</th><th>Curso nombre</th>" \
                 "<th>progreso (%)</th></tr>"
        for (n, p, u, c, cn) in zip(nombre, percentage, usiario_ids, curso_id, curso_nombre):
            result += "<tr><td>" + str(u[0]) + "</td><td>" + n[0] + "</td><td>" + str(c[0]) + "</td><td>" + str(cn[0]) +\
                      "</td><td>" + str(p) + "</td>"
            result += "<tr></tr>"
        result += "</table>"
        conn.close()
        Variables.analitica_video = result
        return render_template("index.html", title="Analitica Video", content=result)


if __name__ == '__main__':
    app.run()
