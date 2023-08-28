import os
import matplotlib.pyplot as plt


def generar_grafico():
    # Datos del gráfico
    x = ['A', 'B', 'C', 'D', 'E']
    y = [20, 35, 30, 25, 40]
    objetivo = 28

    # Crear el gráfico de barras
    plt.bar(x, y)

    # Mostrar los valores encima de las barras
    for i, v in enumerate(y):
        plt.text(i, v, str(v), ha='center', va='bottom')

    # Añadir la línea de objetivo
    plt.axhline(y=objetivo, color='red', linestyle='--', label='Objetivo')

    # Ajustar los límites de los ejes x e y
    plt.xlim(-0.5, len(x) - 0.5)
    plt.ylim(0, max(y) + 5)

    # Eliminar los bordes del gráfico
    plt.box(False)

    # Obtener la ruta absoluta del directorio "app budget/src/static/img"
    img_folder = os.path.abspath(os.path.join(
        os.getcwd(), '..', 'static', 'img'))

    # Crear el directorio "app budget/src/static/img" si no existe
    os.makedirs(img_folder, exist_ok=True)

    # Guardar el gráfico como archivo en el directorio "app budget/src/static/img"
    img_path = os.path.join(img_folder, 'grafico.png')
    plt.savefig(img_path, bbox_inches='tight', pad_inches=0)
