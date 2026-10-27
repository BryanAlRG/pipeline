"""Cliente extractor: consulta CoinGecko y envía el payload al microservicio."""
import argparse
import json
import os
import urllib.request
from datetime import datetime, timezone

COINGECKO_URL = (
    "https://api.coingecko.com/api/v3/coins/markets"
    "?vs_currency=usd&order=market_cap_desc&per_page=10&page=1"
    "&sparkline=false&price_change_percentage=24h"
)

def get_json(url, timeout=20):
    req = urllib.request.Request(url, headers={"User-Agent": "CloudMiningPractice/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--service-url", default=os.getenv("SERVICE_URL", "http://127.0.0.1:8080"))
    parser.add_argument("--input-json", help="Usa un archivo JSON local en lugar de llamar a CoinGecko")
    args = parser.parse_args()

    if args.input_json:
        with open(args.input_json, encoding="utf-8") as f:
            raw = json.load(f)
    else:
        raw = get_json(COINGECKO_URL)

    payload = json.dumps({"data": raw}).encode("utf-8")
    req = urllib.request.Request(
        args.service_url.rstrip("/") + "/analyze",
        data=payload,
        headers={"Content-Type": "application/json", "User-Agent": "CloudMiningPractice/1.0"},
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=30) as response:
        result = json.loads(response.read().decode("utf-8"))
    result["source"] = "local_fixture" if args.input_json else "CoinGecko API"
    result["extracted_at"] = datetime.now(timezone.utc).isoformat()
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
