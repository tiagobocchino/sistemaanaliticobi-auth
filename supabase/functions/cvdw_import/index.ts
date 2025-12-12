// Supabase Edge Function: cvdw_import
// Roda com cron (Scheduled Functions). Coleta dados do CVDW e faz upsert nas tabelas.
// Configure variáveis em supabase secrets:
//   CVDW_EMAIL, CVDW_TOKEN, CVDW_BASE (opcional, default do CVDW)
//   SUPABASE_SERVICE_ROLE_KEY (ou usar a chave padrão de função se permissões bastarem)
// Agende via supabase functions deploy + scheduled.

import { serve } from "https://deno.land/std@0.177.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2.44.4";

const SUPABASE_URL = Deno.env.get("SUPABASE_URL")!;
const SUPABASE_SERVICE_ROLE_KEY = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY") ?? Deno.env.get("SUPABASE_ANON_KEY")!;
const CVDW_BASE = Deno.env.get("CVDW_BASE") ?? "https://bpincorporadora.cvcrm.com.br/api/v1/cvdw";
const CVDW_EMAIL = Deno.env.get("CVDW_EMAIL")!;
const CVDW_TOKEN = Deno.env.get("CVDW_TOKEN")!;

const ENDPOINTS: Record<string, string> = {
  reservas: "reservas",
  vendas: "vendas",
  unidades: "unidades",
  leads: "leads",
  imobiliarias: "imobiliarias",
  corretores: "corretores",
  repasses: "repasses",
  pessoas: "pessoas",
  // comissoes: "comissoes", // habilitar quando a API estiver estável
};

const PAGE_SIZE = 500;
const BACKOFFS = [60, 120, 180, 240, 300]; // segundos

const sb = createClient(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY);

async function fetchPage(endpoint: string, page: number) {
  let attempt = 0;
  while (true) {
    const url = `${CVDW_BASE}/${endpoint}?registros_por_pagina=${PAGE_SIZE}&pagina=${page}`;
    const resp = await fetch(url, {
      headers: {
        accept: "application/json",
        "content-type": "application/json",
        email: CVDW_EMAIL,
        token: CVDW_TOKEN,
      },
    });
    if ([429, 500].includes(resp.status)) {
      const wait = BACKOFFS[attempt] ?? BACKOFFS[BACKOFFS.length - 1];
      attempt += 1;
      if (attempt > BACKOFFS.length) {
        throw new Error(`${endpoint} página ${page} falhou após backoff (status ${resp.status})`);
      }
      await new Promise((r) => setTimeout(r, wait * 1000));
      continue;
    }
    if (!resp.ok) {
      const txt = await resp.text();
      throw new Error(`${endpoint} página ${page} status ${resp.status}: ${txt}`);
    }
    const json = await resp.json();
    if (json && typeof json === "object" && Array.isArray(json.dados)) {
      return json as { dados: any[]; total_de_paginas?: number };
    }
    // fallback se a API retornar lista direta
    return { dados: Array.isArray(json) ? json : [], total_de_paginas: 1 };
  }
}

function chunk<T>(arr: T[], size: number) {
  const out: T[][] = [];
  for (let i = 0; i < arr.length; i += size) out.push(arr.slice(i, i + size));
  return out;
}

async function importEndpoint(ep: string, table: string) {
  let page = 1;
  let total = 1;
  let imported = 0;
  while (page <= total) {
    const payload = await fetchPage(ep, page);
    const rows = payload.dados ?? [];
    total = payload.total_de_paginas ?? total;
    if (rows.length === 0) break;
    const mapped = rows.map((r: any) => {
      const obj: Record<string, any> = { raw: r };
      // tenta identificar chaves comuns
      for (const key of ["id", "idreserva", "idlead", "idunidade", "idimobiliaria", "idcorretor", "idrepasse", "idpessoa"]) {
        if (r[key] !== undefined) {
          obj[key] = r[key];
          break;
        }
      }
      return obj;
    });
    for (const c of chunk(mapped, 500)) {
      const { error } = await sb.from(table).upsert(c);
      if (error) throw new Error(`Erro upsert ${table} p${page}: ${error.message}`);
    }
    imported += rows.length;
    page += 1;
    // pequena folga entre páginas
    await new Promise((r) => setTimeout(r, 500));
  }
  return imported;
}

serve(async () => {
  try {
    const results: Record<string, any> = {};
    for (const [table, ep] of Object.entries(ENDPOINTS)) {
      const count = await importEndpoint(ep, table);
      results[table] = { imported: count };
    }
    return new Response(JSON.stringify({ ok: true, results }, null, 2), { headers: { "content-type": "application/json" } });
  } catch (e) {
    return new Response(JSON.stringify({ ok: false, error: String(e) }, null, 2), { status: 500, headers: { "content-type": "application/json" } });
  }
});
