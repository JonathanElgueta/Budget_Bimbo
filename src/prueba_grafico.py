import matplotlib.pyplot as plt
import pyodbc
from config import config
from flask import Flask, render_template, request, redirect, url_for, flash, send_file


# Establecer la conexión a la base de datos
app = Flask(__name__)
app.config.from_object(config['development'])
db = pyodbc.connect(
    f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={app.config["MSSQL_SERVER"]};DATABASE={app.config["MSSQL_DATABASE"]};Trusted_Connection={app.config["MSSQL_TRUSTED_CONNECTION"]}'
)
cursor = db.cursor()

# Ejecutar el procedimiento almacenado para obtener los datos
cursor.execute("EXECUTE ObtenerSalasporCadena;")
results = cursor.fetchall()

# Obtener los datos de las salas
salas = [row[0] for row in results]
cantidades = [row[1] for row in results]

# Crear el gráfico de línea
# Ajustar el tamaño del gráfico según tus necesidades
plt.figure(figsize=(12, 6))
# Utilizar marcadores 'o' para resaltar los puntos
plt.plot(salas, cantidades, marker='o')

# Añadir etiquetas y título
plt.xlabel('Salas')
plt.ylabel('Cantidad de Salas')
plt.title('Salas por Cadena')

# Mostrar el gráfico
plt.show()

# Cerrar la conexión a la base de datos
cursor.close()
db.close()
