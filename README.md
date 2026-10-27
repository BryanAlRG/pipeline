# Pipeline distribuido de minería de datos (CoinGecko)

## Arquitectura
1. `fetcher.py` extrae los 10 activos principales desde CoinGecko (API pública).
2. Envía el payload JSON al endpoint HTTP `POST /analyze`.
3. `app.py` limpia texto, convierte campos numéricos y aplica reglas de clasificación.
4. Devuelve JSON consolidado con etiquetas y timestamp.
5. `render.yaml` permite desplegar el microservicio como servicio web en Render.

> La extracción en vivo depende de disponibilidad y límites de CoinGecko. La práctica no debe interpretarse como recomendación de inversión.

## Ejecutar localmente
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python app.py
```
En otra terminal:
```bash
python fetcher.py
```
Esto consulta CoinGecko y requiere acceso a Internet. Para probar sin Internet:
```bash
python fetcher.py --input-json sample_input.json
```

## Probar API manualmente
```bash
curl http://127.0.0.1:8080/health
curl -X POST http://127.0.0.1:8080/analyze -H "Content-Type: application/json" -d @sample_input.json
```

## Despliegue en Render
1. Sube el contenido de esta carpeta a un repositorio Git.
2. En Render, selecciona **New + → Blueprint** y conecta el repositorio que contiene `render.yaml`.
3. Confirma la creación del servicio y espera a que el deploy finalice.
4. Comprueba `https://TU-SERVICIO.onrender.com/health`.
5. Ejecuta `python fetcher.py --service-url https://TU-SERVICIO.onrender.com`.
No publiques secretos ni datos sensibles. Esta aplicación no necesita una clave API para el endpoint público usado, aunque el proveedor puede aplicar límites.

## Reglas de clasificación
- Cambio 24 h >= +3% → `tendencia_alcista`
- Cambio 24 h <= -3% → `tendencia_bajista`
- En otro caso → `estable`

## Limitaciones
Es un prototipo didáctico con reglas deterministas, no un modelo entrenado. Los valores faltantes se imputan con 0 en campos numéricos. Para producción se recomienda validar esquema, registrar errores, aplicar límites de tamaño, autenticación, reintentos y monitoreo.
