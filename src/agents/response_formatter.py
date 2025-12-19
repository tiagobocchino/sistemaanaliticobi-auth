"""
Formatador de respostas do agente IA para linguagem natural e profissional.
Transforma respostas técnicas em comunicação de negócios clara e acionável.
"""
from typing import Dict, Any, List, Optional


class ResponseFormatter:
    """
    Formata respostas do agente para serem naturais, profissionais e didáticas.
    Remove jargão técnico e apresenta insights como um analista sênior.
    """

    @staticmethod
    def format_business_response(
        question: str,
        data: Dict[str, Any],
        insights: Optional[List[str]] = None,
        recommendations: Optional[List[str]] = None
    ) -> str:
        """
        Formata uma resposta de negócios de forma profissional.

        Args:
            question: Pergunta original do usuário
            data: Dados brutos da análise
            insights: Lista de insights gerados
            recommendations: Lista de recomendações

        Returns:
            String formatada em linguagem natural
        """
        parts = []

        # Contextualização inicial
        if "vendas" in question.lower() or "venda" in question.lower():
            parts.append("Analisando os dados de vendas disponíveis:")
        elif "cliente" in question.lower():
            parts.append("Com base no perfil dos clientes:")
        elif "financeiro" in question.lower() or "contas" in question.lower():
            parts.append("Observando a situação financeira:")
        elif "oportunidade" in question.lower():
            parts.append("Analisando o pipeline de oportunidades:")
        else:
            parts.append("Aqui está o que encontrei:")

        # Apresentar dados de forma natural
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, (int, float)):
                    metric_name = ResponseFormatter._humanize_metric_name(key)
                    formatted_value = ResponseFormatter._format_value(value)
                    parts.append(f"• {metric_name}: {formatted_value}")
                elif isinstance(value, dict):
                    # Dados aninhados
                    source_name = key.upper()
                    parts.append(f"\n**Fonte: {source_name}**")
                    for subkey, subvalue in value.items():
                        if isinstance(subvalue, (int, float)):
                            metric_name = ResponseFormatter._humanize_metric_name(subkey)
                            formatted_value = ResponseFormatter._format_value(subvalue)
                            parts.append(f"  • {metric_name}: {formatted_value}")

        # Insights (se houver)
        if insights and len(insights) > 0:
            parts.append("\n**Principais Insights:**")
            for insight in insights:
                parts.append(f"✓ {insight}")

        # Recomendações (se houver)
        if recommendations and len(recommendations) > 0:
            parts.append("\n**Recomendações:**")
            for i, rec in enumerate(recommendations, 1):
                parts.append(f"{i}. {rec}")

        return "\n".join(parts)

    @staticmethod
    def _humanize_metric_name(key: str) -> str:
        """Converte nome técnico de métrica para linguagem natural."""
        mappings = {
            # Vendas
            "quantidade_vendas": "Total de vendas",
            "valor_total": "Valor total",
            "oportunidades_abertas": "Oportunidades em andamento",
            "taxa_conversao": "Taxa de conversão",
            "valor_pipeline": "Valor em pipeline",
            "ticket_medio": "Ticket médio",

            # Financeiro
            "contas_pagar": "Contas a pagar",
            "contas_receber": "Contas a receber",
            "saldo": "Saldo",
            "fluxo_caixa": "Fluxo de caixa",

            # Métricas gerais
            "media": "Média",
            "count": "Quantidade",
            "total": "Total",
            "quantidade": "Quantidade",
            "percentual": "Percentual",
        }
        return mappings.get(key, key.replace("_", " ").title())

    @staticmethod
    def _format_value(value: Any) -> str:
        """Formata valores para apresentação profissional."""
        if isinstance(value, float):
            # Se for um percentual (valor entre 0 e 1)
            if 0 <= value <= 1:
                return f"{value * 100:.1f}%"
            # Se for um valor monetário (assumir se > 100)
            elif value > 100:
                return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            else:
                return f"{value:.2f}"
        elif isinstance(value, int):
            if value > 1000:
                return f"{value:,}".replace(",", ".")
            return str(value)
        return str(value)

    @staticmethod
    def create_system_prompt(context: Dict[str, Any]) -> str:
        """
        Cria um system prompt profissional que instrui o agente a responder
        como um analista de negócios sênior.
        """
        apis_str = ", ".join(context.get("available_apis", [])) or "base de dados interna"

        return f"""Você é um Analista de Negócios Sênior especializado em análise de dados empresariais.

IDENTIDADE E ESTILO:
- Você é um profissional experiente que interpreta dados e gera insights acionáveis
- Comunique-se de forma clara, objetiva e profissional
- Use linguagem de negócios, não jargão técnico
- Seja didático ao explicar conceitos complexos
- Contextualize os números com significado empresarial

FONTES DE DADOS DISPONÍVEIS:
{apis_str}

REGRAS CRÍTICAS - NUNCA FAÇA ISSO:
❌ NÃO mostre código (curl, Python, SQL, etc.)
❌ NÃO exiba JSON bruto ou estruturas de dados
❌ NÃO mencione nomes técnicos de APIs ou endpoints
❌ NÃO mostre detalhes de implementação ou configuração
❌ NÃO use linguagem técnica de programação
❌ NÃO mostre blocos de código markdown (```json, ```python, etc.)

COMO VOCÊ DEVE RESPONDER:
✓ Use linguagem natural e profissional
✓ Apresente números formatados (R$ 1.234,56 ou 45,3%)
✓ Contextualize métricas com significado de negócio
✓ Ofereça insights além dos números brutos
✓ Sugira ações práticas quando relevante
✓ Compare períodos ou padrões quando possível
✓ Seja conversacional mas profissional

ESTRUTURA DE RESPOSTA IDEAL:
1. Contextualização breve (1 frase sobre o que está sendo analisado)
2. Dados principais em bullet points formatados
3. Insights ou observações importantes
4. Recomendações práticas (quando aplicável)

EXEMPLOS DE BOAS RESPOSTAS:

Pergunta: "Quantas vendas temos?"
✓ BOA RESPOSTA:
"Analisando os dados de vendas, identifico 45 vendas concluídas neste período. Este volume representa um crescimento de 12% em relação ao mês anterior, indicando uma tendência positiva no desempenho comercial.

**Recomendação:** Manter o ritmo atual e analisar quais estratégias contribuíram para esse crescimento."

❌ RESPOSTA RUIM:
"```json
{{'vendas': 45}}
```
A API /vendas retornou 45 registros usando o endpoint GET /api/vendas."

Pergunta: "Como está o financeiro?"
✓ BOA RESPOSTA:
"A situação financeira atual apresenta um cenário saudável:

• Contas a receber: R$ 125.340,00
• Contas a pagar: R$ 89.200,00
• Saldo positivo: R$ 36.140,00

O fluxo de caixa está equilibrado, com mais entradas previstas do que saídas. Este saldo positivo oferece margem de segurança para operações do próximo mês.

**Recomendação:** Manter o acompanhamento semanal para garantir a liquidez e considerar antecipar cobranças de valores maiores."

❌ RESPOSTA RUIM:
"```
curl -X POST http://api/financeiro
Response: {{'contas_receber': 125340, 'contas_pagar': 89200}}
```
Usando a tool fetch_data_from_api('sienge', '/financeiro')..."

CONTEXTO DA CONSULTA ATUAL:
- Usuário: {context.get('user_id', 'desconhecido')}
- Nível de acesso: {context.get('permissions', {}).get('nivel_acesso', 'básico')}

Responda SEMPRE como um analista sênior conversando com um stakeholder de negócios.
Foque em SIGNIFICADO e AÇÃO, não em tecnologia.
Seja humano, profissional e útil."""

    @staticmethod
    def extract_insights_from_data(data: Dict[str, Any], intent: str) -> List[str]:
        """
        Extrai insights automáticos baseado nos dados e intenção.
        """
        insights = []

        if intent == "vendas":
            if "oportunidades_abertas" in data:
                count = data["oportunidades_abertas"]
                if count > 50:
                    insights.append(f"Volume alto de oportunidades ({count}) indica demanda forte no mercado")
                elif count < 10:
                    insights.append(f"Volume baixo de oportunidades ({count}) sugere necessidade de intensificar prospecção")

            if "taxa_conversao" in data:
                rate = data["taxa_conversao"]
                if rate > 0.30:
                    insights.append(f"Taxa de conversão de {rate*100:.1f}% está acima da média do setor (20-25%)")
                elif rate < 0.15:
                    insights.append(f"Taxa de conversão de {rate*100:.1f}% sugere oportunidade de melhoria no processo de vendas")

            if "valor_pipeline" in data:
                pipeline = data["valor_pipeline"]
                if pipeline > 1000000:
                    insights.append(f"Pipeline robusto de R$ {pipeline:,.2f} indica potencial de faturamento forte")

        elif intent == "financeiro":
            if "contas_pagar" in data and "contas_receber" in data:
                cp = data["contas_pagar"]
                cr = data["contas_receber"]
                saldo = cr - cp
                if saldo > 0:
                    insights.append(f"Fluxo de caixa positivo em R$ {saldo:,.2f} oferece margem de segurança")
                else:
                    insights.append(f"Atenção: fluxo negativo de R$ {abs(saldo):,.2f} requer ação imediata")

        return insights

    @staticmethod
    def generate_recommendations(data: Dict[str, Any], intent: str) -> List[str]:
        """
        Gera recomendações automáticas baseadas nos dados.
        """
        recommendations = []

        if intent == "vendas":
            if "taxa_conversao" in data:
                rate = data["taxa_conversao"]
                if rate < 0.20:
                    recommendations.append("Revisar processo de qualificação de leads para aumentar taxa de conversão")
                    recommendations.append("Implementar treinamento focado em técnicas de fechamento para a equipe")

            if "oportunidades_abertas" in data:
                count = data["oportunidades_abertas"]
                if count > 100:
                    recommendations.append("Considerar expandir equipe comercial para atender volume crescente de demanda")
                elif count < 15:
                    recommendations.append("Intensificar ações de prospecção e marketing para gerar mais oportunidades")

            if "valor_pipeline" in data and "oportunidades_abertas" in data:
                pipeline = data["valor_pipeline"]
                count = data["oportunidades_abertas"]
                if count > 0:
                    ticket_medio = pipeline / count
                    if ticket_medio < 10000:
                        recommendations.append("Focar em oportunidades de maior ticket para otimizar resultado da equipe")

        elif intent == "financeiro":
            if "contas_pagar" in data and "contas_receber" in data:
                cp = data["contas_pagar"]
                cr = data["contas_receber"]
                if cp > cr:
                    recommendations.append("Priorizar cobrança de valores em atraso para equilibrar fluxo de caixa")
                    recommendations.append("Avaliar possibilidade de renegociar prazos com fornecedores principais")
                elif cr > cp * 1.5:
                    recommendations.append("Saldo confortável permite considerar investimentos estratégicos")

        return recommendations


# Singleton global
response_formatter = ResponseFormatter()
