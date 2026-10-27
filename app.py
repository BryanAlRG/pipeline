import math
import os
import re
from datetime import datetime, timezone
from flask import Flask, jsonify, request

app = Flask(__name__)

def clean_text(value):
    """Normaliza texto, elimina caracteres de control y compacta espacios."""
    if value is None:
        return ""
    value = str(value)
    value = re.sub(r"[\x00-\x1f\x7f]", " ", value)
    value = re.sub(r"[^\w\s\-\.\$]", "", value, flags=re.UNICODE)
    return re.sub(r"\s+", " ", value).strip()

def to_number(value, default=0.0):
    try:
        number = float(value)
        return number if math.isfinite(number) else default
    except (TypeError, ValueError):
        return default

def analyze_coin(raw):
    """Limpieza + reglas de scoring demostrativas; no es asesoramiento financiero."""
    name = clean_text(raw.get("name", "desconocido")) or "desconocido"
    symbol = clean_text(raw.get("symbol", "")).upper()
    price = max(0.0, to_number(raw.get("current_price")))
    change = to_number(raw.get("price_change_percentage_24h"))
    market_cap = max(0.0, to_number(raw.get("market_cap")))
    # Regla de ejemplo: etiqueta basada únicamente en cambio porcentual 24 h.
    if change >= 3:
        label = "tendencia_alcista"
    elif change <= -3:
        label = "tendencia_bajista"
    else:
        label = "estable"
    return {
        "id": clean_text(raw.get("id", "")),
        "name": name,
        "symbol": symbol,
        "current_price_usd": round(price, 8),
        "change_24h_pct": round(change, 4),
        "market_cap_usd": round(market_cap, 2),
        "label": label,
        "rule": "change_24h_pct >= 3: tendencia_alcista; <= -3: tendencia_bajista; otro: estable"
    }

@app.get("/health")
def health():
    return jsonify({"status": "ok", "service": "cloud-mining-api"})

@app.post("/analyze")
def analyze():
    payload = request.get_json(silent=True)
    if payload is None:
        return jsonify({"error": "Se requiere un JSON válido"}), 400
    items = payload if isinstance(payload, list) else payload.get("data", [])
    if not isinstance(items, list):
        return jsonify({"error": "El campo 'data' debe ser una lista"}), 400
    results = [analyze_coin(item) for item in items if isinstance(item, dict)]
    return jsonify({
        "pipeline": "coin-gecko-serverless-mining",
        "processed_at": datetime.now(timezone.utc).isoformat(),
        "input_count": len(items),
        "output_count": len(results),
        "results": results
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "8080")))
