# Exemplos de Perguntas que Podem ser Feitas ao Sistema

Agora que o sistema esta 100% operacional, voce pode fazer perguntas em **linguagem natural** e o agente IA vai:
1. Entender sua pergunta
2. Consultar os dados RAW das tabelas corretas
3. Aplicar filtros e agregacoes
4. Retornar a resposta formatada

---

## Perguntas Sobre Leads

- "Quantos leads ativos temos?"
- "Me mostre os 10 ultimos leads cadastrados"
- "Quantos leads estao em cada situacao?"
- "Quais leads estao na BASE FRIA?"
- "Me mostre leads de Brasilia"

## Perguntas Sobre Vendas

- "Quantas vendas foram realizadas?"
- "Me mostre as ultimas 5 vendas"
- "Quantas vendas ativas temos?"
- "Qual o valor total das vendas?"

## Perguntas Sobre Corretores

- "Quantos corretores ativos temos?"
- "Me mostre a lista de corretores"
- "Quais corretores tem mais vendas?"
- "Me mostre os dados do corretor X"

## Perguntas Sobre Unidades

- "Quantas unidades disponiveis temos?"
- "Me mostre unidades do bloco A"
- "Quantas unidades por andar?"
- "Quais unidades ainda nao foram vendidas?"

## Perguntas Sobre Reservas

- "Quantas reservas ativas temos?"
- "Me mostre as ultimas reservas"
- "Quais reservas estao pendentes?"

## Perguntas Sobre Pessoas

- "Quantas pessoas estao cadastradas?"
- "Me mostre pessoas de Brasilia"
- "Quantos clientes ativos temos?"

## Perguntas Sobre Imobiliarias

- "Quantas imobiliarias parceiras temos?"
- "Me mostre as imobiliarias ativas"

## Perguntas Sobre Repasses

- "Quantos repasses foram feitos?"
- "Me mostre os ultimos repasses"

---

## Perguntas Complexas (Multiplas Tabelas)

- "Quantas vendas o corretor X realizou?"
- "Qual a taxa de conversao de leads para vendas?"
- "Me mostre um dashboard de vendas"
- "Qual o ranking de corretores por vendas?"
- "Quantos leads viraram vendas?"

---

## Como o Sistema Funciona

1. **Voce faz a pergunta** em linguagem natural
2. **O agente IA analisa** e identifica:
   - Qual tabela consultar (leads, vendas, corretores, etc)
   - Quais filtros aplicar
   - Que campos retornar
3. **Executa a tool `query_raw_data`** com os parametros corretos
4. **Filtra dados sensiveis** (CPF, email, telefone sao mascarados)
5. **Retorna a resposta** formatada e explicada

---

## Indices GIN (Performance)

Os indices GIN foram criados nas 8 tabelas:
- idx_leads_raw
- idx_vendas_raw
- idx_reservas_raw
- idx_unidades_raw
- idx_corretores_raw
- idx_pessoas_raw
- idx_imobiliarias_raw
- idx_repasses_raw

Isso significa que **buscas no campo RAW (JSONB) sao ultra-rapidas**!

---

## Seguranca

- ✅ Dados sensiveis sao mascarados automaticamente
- ✅ Apenas tabelas permitidas sao acessadas
- ✅ Limite maximo de 500 registros por consulta
- ✅ Apenas colunas permitidas podem ser filtradas

---

## Pronto para Comecar!

Faca sua primeira pergunta:

**"Quantos leads ativos temos?"**
