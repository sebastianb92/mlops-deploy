from flask import Flask, render_template, request
from datetime import datetime
import os
import csv

# === CONFIGURACIÓN DE ARCHIVOS ===
LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "predicciones.csv")
os.makedirs(LOG_DIR, exist_ok=True)

app = Flask(__name__)

def asegurar_archivo_csv():
    """Crea el archivo de logs si no existe, con encabezados."""
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["fecha", "edad", "pcr", "fc", "resultado"])

# === RUTA PRINCIPAL ===
@app.route('/')
def home():
    return render_template('index.html')

# === RUTA DE PREDICCIÓN ===
@app.route('/predecir', methods=['POST'])
def predecir():
    # Soporte para JSON y formulario web
    if request.is_json:
        data = request.get_json()
        edad = int(data.get('edad', 0))
        pcr = float(data.get('pcr', 0))
        fc = int(data.get('fc', 0))
    else:
        edad = int(request.form.get('edad', 0))
        pcr = float(request.form.get('pcr', 0))
        fc = int(request.form.get('fc', 0))

    # Simulación de un modelo con 5 categorías clínicas
    if pcr < 3 and fc < 90 and edad < 50:
        resultado = "NO ENFERMO"
    elif 3 <= pcr < 10 or 90 <= fc < 110:
        resultado = "ENFERMEDAD LEVE"
    elif 10 <= pcr < 20 or 110 <= fc < 130:
        resultado = "ENFERMEDAD AGUDA"
    elif 20 <= pcr < 25 or 130 <= fc < 150:
        resultado = "ENFERMEDAD CRÓNICA"
    else:
        resultado = "ENFERMEDAD TERMINAL"

    # Asegurar archivo antes de escribir
    asegurar_archivo_csv()

    # Guardar predicción en CSV
    with open(LOG_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            edad, pcr, fc, resultado
        ])

    # Si la petición vino desde JSON (como en los tests), devolvemos JSON
    if request.is_json:
        return {"resultado": resultado}, 200

    # Si vino desde el navegador, renderizamos la plantilla
    return render_template('index.html', resultado=resultado)

# === RUTA DE HISTORIAL (VISUAL) ===
@app.route('/historial')
def historial():
    asegurar_archivo_csv()

    data = []
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append(row)

    if not data:
        return render_template(
            'historial.html',
            total_por_categoria={},
            ultimas_predicciones=[],
            fecha_ultima="Sin registros"
        )

    # Cálculos estadísticos
    total_por_categoria = {}
    for row in data:
        cat = row["resultado"]
        total_por_categoria[cat] = total_por_categoria.get(cat, 0) + 1

    ultimas_predicciones = data[-5:][::-1] if len(data) >= 5 else data[::-1]
    fecha_ultima = data[-1]["fecha"]

    return render_template(
        'historial.html',
        total_por_categoria=total_por_categoria,
        ultimas_predicciones=ultimas_predicciones,
        fecha_ultima=fecha_ultima
    )

# === MODO SERVICIO ===
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
