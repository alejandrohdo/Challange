from variables import *
import os
import re
import sqlite3
import pandas as pd


def import_db():
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
