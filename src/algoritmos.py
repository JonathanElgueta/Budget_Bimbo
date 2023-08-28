import pyodbc
from config import config
from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from openpyxl import Workbook


def connect_to_database():
    app = Flask(__name__)
    app.config.from_object(config['development'])
    return pyodbc.connect(
        f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={app.config["MSSQL_SERVER"]};DATABASE={app.config["MSSQL_DATABASE"]};Trusted_Connection={app.config["MSSQL_TRUSTED_CONNECTION"]}'
    )


def get_month_number(month_string):
    db = connect_to_database()
    cursor = db.cursor()
    cursor.execute(f"SELECT MONTH('{month_string} 1, 2023')")
    resultado = cursor.fetchone()
    db.close()
    return resultado[0] - 3, resultado[0] - 1


def fetch_data(month_inicio, month_fin):
    db = connect_to_database()
    cursor = db.cursor()
    consulta = """
    SELECT c.Cliente_id AS [Codigo Cliente],
           c.Nombre_Sala AS [Nombre Cliente],
           FLOOR(SUM(v.Venta_Neta_$) / 3) AS PromedioVentasUltimos3Meses
    FROM Ventas v
    JOIN Cliente c ON v.Cliente_id = c.Cliente_id
    WHERE MONTH(v.Fecha) >= ? AND MONTH(v.Fecha) <= ?
    GROUP BY c.Cliente_id, c.Nombre_Sala
    """
    cursor.execute(consulta, (month_inicio, month_fin))
    resultados = cursor.fetchall()
    db.close()
    return resultados


def generate_excel(resultados, file_path):
    libro = Workbook()
    hoja = libro.active
    hoja.append(["Codigo Cliente", "Nombre Cliente", "Promedio Venta 3 meses"])
    for fila in resultados:
        hoja.append(list(fila))
    libro.save(file_path)


# Obtener el mes seleccionado del usuario
mes_seleccionado = input(
    "Ingrese el mes deseado (en formato 'nombre del mes'): ")

# Obtener el número de mes correspondiente al mes seleccionado
mes_inicio, mes_fin = get_month_number(mes_seleccionado)

# Obtener los resultados de la consulta
resultados = fetch_data(mes_inicio, mes_fin)

# Guardar el libro de Excel
file_path = "C:/Users/jonat/OneDrive/Escritorio/App Budget/downloads/Promedio_ventas_ultimos_3_meses.xlsx"
generate_excel(resultados, file_path)
