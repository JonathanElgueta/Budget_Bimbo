import pandas as pd
import pyodbc
from config import config
from flask import Flask
import calendar
from datetime import datetime, timedelta
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows
import locale
import os


def establish_db_connection():
    app = Flask(__name__)
    app.config.from_object(config['development'])
    db = pyodbc.connect(
        f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={app.config["MSSQL_SERVER"]};DATABASE={app.config["MSSQL_DATABASE"]};Trusted_Connection={app.config["MSSQL_TRUSTED_CONNECTION"]}'
    )
    return db


def get_client_data(db):
    query = '''
    SELECT c.Cliente_id AS [Número de Cliente],
       CONCAT(UPPER(LEFT(c.Nombre_Sala, 1)), LOWER(SUBSTRING(c.Nombre_Sala, 2, LEN(c.Nombre_Sala)))) AS [Nombre de Sala],
       CONCAT(UPPER(LEFT(d.Nombre_One, 1)), LOWER(SUBSTRING(d.Nombre_One, 2, LEN(d.Nombre_One))), ' ', 
              UPPER(LEFT(d.ApellidoP, 1)), LOWER(SUBSTRING(d.ApellidoP, 2, LEN(d.ApellidoP)))) AS [Nombre del Divisional],
       CONCAT(UPPER(LEFT(s.Nombre_One, 1)), LOWER(SUBSTRING(s.Nombre_One, 2, LEN(s.Nombre_One))), ' ', 
              UPPER(LEFT(s.ApellidoP, 1)), LOWER(SUBSTRING(s.ApellidoP, 2, LEN(s.ApellidoP)))) AS [Nombre del Supervisor],
       CONCAT(UPPER(LEFT(ca.Formato, 1)), LOWER(SUBSTRING(ca.Formato, 2, LEN(ca.Formato)))) AS [Cadena],
       CONCAT(UPPER(LEFT(ca.Nombre_Cadena, 1)), LOWER(SUBSTRING(ca.Nombre_Cadena, 2, LEN(ca.Nombre_Cadena)))) AS [Formato Cadena],
       CONCAT(UPPER(LEFT(k.Nombre_One, 1)), LOWER(SUBSTRING(k.Nombre_One, 2, LEN(k.Nombre_One))), ' ', 
              UPPER(LEFT(k.ApellidoP, 1)), LOWER(SUBSTRING(k.ApellidoP, 2, LEN(k.ApellidoP)))) AS [Nombre del Kam]
    FROM Cliente c
    JOIN Cadena ca ON ca.Cadena_id = c.Cadena_id
    JOIN Agencia a ON a.Agencia_id = c.Agencia_id
    JOIN Supervisor s ON s.Supervisor_id = c.Supervisor_id
    JOIN Divisional d ON d.Divisional_id = c.Divisional_id
    JOIN Kam k ON k.Kam_id = c.Kam_id
    ORDER BY c.Cliente_id ASC
    '''
    df_clientes = pd.read_sql_query(query, db)
    return df_clientes


def get_sales_data(db):
    query = '''
    SELECT CONVERT(varchar, Fecha, 103) AS FechaInvertida, FLOOR(SUM(Venta_Neta_$)) AS VentasPorDia
    FROM Ventas
    GROUP BY Fecha
    ORDER BY Fecha
    '''
    df_ventas = pd.read_sql_query(query, db)
    return df_ventas


def generate_dates(nombre_mes, cantidad_dias):
    # Establecer el idioma español para el formato de fecha y codificación UTF-8
    locale.setlocale(locale.LC_TIME, 'es_ES.utf8')
    locale.setlocale(locale.LC_ALL, 'es_ES.utf8')

    meses = {
        'Enero': 1,
        'Febrero': 2,
        'Marzo': 3,
        'Abril': 4,
        'Mayo': 5,
        'Junio': 6,
        'Julio': 7,
        'Agosto': 8,
        'Septiembre': 9,
        'Octubre': 10,
        'Noviembre': 11,
        'Diciembre': 12
    }

    mes_numero = meses[nombre_mes]

    # Crear la fecha inicial y agregar los días
    fecha_inicial = datetime(2023, mes_numero, 1)
    fechas = [fecha_inicial + timedelta(days=i) for i in range(cantidad_dias)]

    # Obtener el nombre del día de la semana en español
    dias_semana = [fecha.strftime('%A').capitalize() for fecha in fechas]

    return fechas, dias_semana


def generate_combined_dataframe(df_clientes, fechas, dias_semana):
    df_base_ejemplo = pd.DataFrame(
        columns=['Fecha', 'DiaSemana', 'Numero Cliente', 'Nombre Sala', 'Nombre Divisional', 'Nombre Supervisor', 'Cadena', 'Formato', 'Nombre Kam'])

    for _, cliente in df_clientes.iterrows():
        # Verificar si el cliente debe ser excluido
        if cliente['Número de Cliente'] not in [98000538, 98007326, 98007328, 981000000149, 981000012984, 981400000001, 981700099053, 983000000003, 983100000003, 983200000003, 983600000003, 983700000003, 983800001312, 983900000003, 984000000003, 984100000003, 984400000001, 985300000001, 98032588, 98032590, 985100000641, 98008398, 98016751, 983000000002, 983800000003, 983900000002, 984100000002, 985300000018, 983600000002, 983700000002, 985000000003, 985200000362, 98007434]:
            data = {
                'Fecha': [fecha.strftime('%d-%m-%Y') for fecha in fechas],
                'DiaSemana': dias_semana,
                'Numero Cliente': cliente['Número de Cliente'],
                'Nombre Sala': cliente['Nombre de Sala'],
                'Nombre Divisional': cliente['Nombre del Divisional'],
                'Nombre Supervisor': cliente['Nombre del Supervisor'],
                'Cadena': cliente['Cadena'],
                'Formato': cliente['Formato Cadena'],
                'Nombre Kam': cliente['Nombre del Kam']
            }

            df_cliente = pd.DataFrame(data)
            df_base_ejemplo = pd.concat(
                [df_base_ejemplo, df_cliente], ignore_index=True)

    # Filtrar los registros que no sean domingos
    df_base_ejemplo = df_base_ejemplo[df_base_ejemplo['DiaSemana'] != 'domingo']

    # Aplicar formato a los nombres en formato Nombre Propio
    df_base_ejemplo['Nombre Sala'] = df_base_ejemplo['Nombre Sala'].apply(
        lambda x: x.title())
    df_base_ejemplo['Nombre Divisional'] = df_base_ejemplo['Nombre Divisional'].apply(
        lambda x: x.title())
    df_base_ejemplo['Nombre Supervisor'] = df_base_ejemplo['Nombre Supervisor'].apply(
        lambda x: x.title())
    df_base_ejemplo['Cadena'] = df_base_ejemplo['Cadena'].apply(
        lambda x: x.title())
    df_base_ejemplo['Nombre Kam'] = df_base_ejemplo['Nombre Kam'].apply(
        lambda x: x.title())

    # Reordenar las columnas
    df_base_ejemplo = df_base_ejemplo.reindex(
        columns=['Fecha', 'DiaSemana', 'Numero Cliente', 'Nombre Sala', 'Nombre Divisional', 'Nombre Supervisor', 'Cadena', 'Formato', 'Nombre Kam'])

    return df_base_ejemplo


def exportar_dataframe_a_excel(df, df_ventas, nombre_archivo):
    # Crear un libro de trabajo de Excel
    libro = Workbook()
    # Crear la primera hoja para los datos de los clientes
    hoja_clientes = libro.active
    hoja_clientes.title = 'Clientes'

    # Escribir los datos de los clientes en la hoja de clientes
    for row in dataframe_to_rows(df, index=False, header=True):
        hoja_clientes.append(row)

    # Crear la segunda hoja para los datos de ventas
    hoja_ventas = libro.create_sheet(title='Ventas')

    # Escribir los datos de ventas en la hoja de ventas
    for row in dataframe_to_rows(df_ventas, index=False, header=True):
        hoja_ventas.append(row)

    # Verificar si el archivo existe y eliminarlo
    if os.path.exists(nombre_archivo):
        os.remove(nombre_archivo)
        print(f'Archivo existente eliminado: {nombre_archivo}')

    # Guardar el libro de trabajo en el archivo Excel
    libro.save(nombre_archivo)
    print(f'Se exportaron los datos al archivo Excel: {nombre_archivo}')


def ejecutar_consulta_y_crear_dataframe():
    db = establish_db_connection()
    df_clientes = get_client_data(db)
    df_ventas = get_sales_data(db)
    nombre_mes = 'Febrero'
    cantidad_dias = calendar.monthrange(2023, 2)[1]
    fechas, dias_semana = generate_dates(nombre_mes, cantidad_dias)
    df_base_ejemplo = generate_combined_dataframe(
        df_clientes, fechas, dias_semana)
    close_db_connection(db)
    return df_base_ejemplo, df_ventas


def close_db_connection(db):
    db.close()


df_clientes, df_ventas = ejecutar_consulta_y_crear_dataframe()
nombre_archivo = 'C:/Users/jonat/OneDrive/Escritorio/App Budget/downloads/Base_Presupuesto.xlsx'
exportar_dataframe_a_excel(df_clientes, df_ventas, nombre_archivo)
