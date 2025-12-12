"""
Importa dados do CVDW para tabelas Supabase já criadas (ver supabase_schema.sql).
Usa backoff para 429/500. Ajuste SUPABASE_URL/KEY no ambiente.
"""
import asyncio
import httpx
import os
from supabase import create_client, Client

HEADERS = {
    "accept": "application/json",
    "content-type": "application/json",
    "email": "tiago.bocchino@4pcapital.com.br",
    "token": "3b10d578dcafe9a615f2471ea1e2f9da5580dc18",
}
BASE = "https://bpincorporadora.cvcrm.com.br/api/v1/cvdw"

ENDPOINTS = {
    "reservas": "reservas",
    "vendas": "vendas",
    "unidades": "unidades",
    "leads": "leads",
    "processos": "processos",
    "imobiliarias": "imobiliarias",
    "corretores": "corretores",
    "repasses": "repasses",
    "pessoas": "pessoas",
    # "comissoes": "comissoes",  # adicionar quando a API responder
}

BACKOFFS = [60, 120, 180, 240, 300]
PAGE_SIZE = 500


def get_supabase_client() -> Client:
    url = os.environ["SUPABASE_URL"]
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ["SUPABASE_ANON_KEY"]
    return create_client(url, key)


async def fetch_page(client: httpx.AsyncClient, ep: str, page: int):
    attempt = 0
    while True:
        resp = await client.get(
            f"{BASE}/{ep}",
            headers=HEADERS,
            params={"registros_por_pagina": PAGE_SIZE, "pagina": page},
        )
        if resp.status_code in (429, 500):
            wait = BACKOFFS[attempt] if attempt < len(BACKOFFS) else BACKOFFS[-1]
            print(f"[{ep}] status {resp.status_code} na página {page}. Aguardando {wait}s...")
            await asyncio.sleep(wait)
            attempt += 1
            if attempt > len(BACKOFFS):
                raise RuntimeError(f"{ep}: excedeu tentativas na página {page} (status {resp.status_code})")
            continue
        resp.raise_for_status()
        data = resp.json()
        if isinstance(data, dict) and "dados" in data and isinstance(data["dados"], list):
            return data
        # caso devolva lista direta
        return {"dados": data, "total_de_paginas": 1}


def chunkify(seq, size):
    for i in range(0, len(seq), size):
        yield seq[i:i + size]


async def import_endpoint(ep: str, table: str, sb: Client):
    async with httpx.AsyncClient(timeout=60) as client:
        page = 1
        total_pages = None
        total_records = 0
        while True:
            payload = await fetch_page(client, ep, page)
            rows = payload.get("dados") or []
            if not rows:
                break
            total_records += len(rows)
            # monta objetos com raw; upsert pelo campo chave quando existir
            payload_db = []
            for r in rows:
                obj = {"raw": r}
                # tenta uma chave plausível
                for key in ("id", "idreserva", "idlead", "idunidade", "idimobiliaria", "idcorretor", "idrepasse", "idpessoa"):
                    if key in r:
                        obj[key] = r[key]
                payload_db.append(obj)
            # upsert em lotes de 500
            for chunk in chunkify(payload_db, 500):
                sb.table(table).upsert(chunk).execute()
            total_pages = payload.get("total_de_paginas") or 1
            print(f"[{ep}] página {page}/{total_pages} importada ({len(rows)} registros)")
            if page >= total_pages:
                break
            page += 1
            await asyncio.sleep(1)
        print(f"[{ep}] total importado: {total_records}")


async def main():
    sb = get_supabase_client()
    for ep, table in ENDPOINTS.items():
        try:
            await import_endpoint(ep, table, sb)
        except Exception as e:
            print(f"Erro ao importar {ep}: {e}")


if __name__ == "__main__":
    asyncio.run(main())
