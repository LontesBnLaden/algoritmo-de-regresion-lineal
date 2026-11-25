# Regresión Lab

Aplicación educativa en español para practicar regresión lineal con dos casos:

- **Precio de terrenos:** estima el precio en soles según el área en metros cuadrados.
- **Ventas mensuales:** predice ventas y proyecta los siguientes seis meses.

Incluye al menos 20 registros por caso, evaluación con R², MAE y RMSE, gráficos, predicción interactiva, edición de la tabla e importación de CSV. También permite descargar el detalle de evaluación de los datos reservados, incluyendo predicción y errores por fila. Los datos incluidos son simulados.

## Inicio rápido en Windows

1. Instala Python 3.10 o posterior.
2. Haz doble clic en `INICIAR.bat`. La primera ejecución crea un entorno local e instala las dependencias; después abre la aplicación en el navegador.

También puedes iniciarla desde una terminal abierta en esta carpeta:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

La aplicación estará disponible en <http://127.0.0.1:8501>.

## Importar un archivo CSV

En la barra lateral, selecciona **Importar CSV**. El archivo debe incluir dos columnas numéricas. Se aceptan encabezados como:

| Caso | Columna de entrada | Columna objetivo |
|---|---|---|
| Terrenos | `Area`, `Area_m2`, `Superficie` | `Precio`, `Costo` |
| Ventas | `Mes`, `Mes_numero`, `Month` | `Ventas`, `Venta` |

Puedes descargar desde la aplicación un CSV de ejemplo, editar la tabla dentro de la interfaz o cargar tu propio archivo. Para la actividad se recomiendan al menos 20 filas válidas por caso.

## Método y lectura de métricas

El caso de terrenos reserva una muestra aleatoria reproducible para evaluar el modelo. Ventas usa los meses finales como prueba para respetar el orden temporal. Se miden R², el error absoluto medio (MAE) y la raíz del error cuadrático medio (RMSE) sobre los datos reservados; después se ajusta el modelo de predicción con todo el historial disponible. MAE resume el error absoluto promedio y RMSE penaliza más los errores grandes. La descarga de evaluación permite revisar valores reales, predicciones y errores fila por fila.

Los ejemplos son deliberadamente simulados y lineales: el caso de terrenos sigue `Precio = 500 × Área + 5.000` y el de ventas `Ventas = 500 × Mes + 2.500`. Estos resultados sirven para comprobar el algoritmo, no como pronósticos comerciales reales. La aplicación advierte sobre las limitaciones de extrapolar y de usar una sola variable.

## Ejecutar pruebas

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```
