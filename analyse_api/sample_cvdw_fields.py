"""
Coleta um sample (primeiro registro) de cada endpoint CVDW para mapear campos.
Respeita rate-limit 429 aguardando 65s antes de tentar novamente.

Uso:
    python analyse_api/sample_cvdw_fields.py

Saída:
    samples_cvdw.json na raiz do repositório com um objeto por endpoint.
"""
import asyncio
import httpx
import json

HEADERS = {
    "accept": "application/json",
    "content-type": "application/json",
    "email": "tiago.bocchino@4pcapital.com.br",
    "token": "3b10d578dcafe9a615f2471ea1e2f9da5580dc18",
}

BASE = "https://bpincorporadora.cvcrm.com.br/api/v1/cvdw"
ENDPOINTS = [
    "comissoes",
    "reservas",
    "vendas",
    "unidades",
    "leads",
    "processos",
    "imobiliarias",
    "corretores",
    "repasses",
    "pessoas",
]


async def fetch_one(ep: str, client: httpx.AsyncClient):
    """
    Busca uma página com 1 registro. Em 429/500 aplica backoff progressivo:
    1 min, 2 min, 3 min, 4 min, 5 min e então aborta.
    """
    backoffs = [60, 120, 180, 240, 300]
    attempt = 0
    while True:
        resp = await client.get(
            f"{BASE}/{ep}",
            headers=HEADERS,
            params={"registros_por_pagina": 1, "pagina": 1},
        )
        if resp.status_code in (429, 500):
            wait = backoffs[attempt] if attempt < len(backoffs) else backoffs[-1]
            print(f"[{ep}] {resp.status_code} recebidos. Aguardando {wait}s antes de tentar novamente (tentativa {attempt+1}).")
            await asyncio.sleep(wait)
            attempt += 1
            if attempt > len(backoffs):
                raise RuntimeError(f"{ep}: excedeu tentativas após backoff progressivo (último status {resp.status_code})")
            continue
        resp.raise_for_status()
        data = resp.json()
        if isinstance(data, dict) and "dados" in data and isinstance(data["dados"], list) and data["dados"]:
            return data["dados"][0]
        return data


async def main():
    samples = {}
    async with httpx.AsyncClient(timeout=60) as client:
        for ep in ENDPOINTS:
            try:
                print(f"Coletando {ep}...")
                samples[ep] = await fetch_one(ep, client)
            except Exception as e:
                samples[ep] = {"error": str(e)}
    with open("samples_cvdw.json", "w", encoding="utf-8") as f:
        json.dump(samples, f, ensure_ascii=False, indent=2)
    print("Samples salvos em samples_cvdw.json")


if __name__ == "__main__":
    asyncio.run(main())
