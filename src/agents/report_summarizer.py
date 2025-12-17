"""
Sumarizador Automático de Relatórios
"""
from typing import Dict, List, Any, Optional
import pandas as pd
from datetime import datetime
import json


class ReportSummarizer:
    """Gera sumários executivos automáticos de dados e análises"""

    def generate_executive_summary(
        self,
        data: Dict[str, Any],
        report_type: str = 'vendas'
    ) -> Dict[str, Any]:
        """
        Gera sumário executivo de alto nível

        Args:
            data: Dados para sumarizar
            report_type: Tipo de relatório ('vendas', 'financeiro', 'clientes', 'geral')

        Returns:
            Sumário executivo estruturado
        """
        try:
            if report_type == 'vendas':
                return self._summarize_sales(data)
            elif report_type == 'financeiro':
                return self._summarize_financial(data)
            elif report_type == 'clientes':
                return self._summarize_customers(data)
            else:
                return self._summarize_general(data)
        except Exception as e:
            return {
                "erro": f"Erro ao gerar sumário: {str(e)}",
                "sumario": "Não foi possível gerar o sumário"
            }

    def _summarize_sales(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Sumário de vendas"""
        summary = {
            'titulo': 'Sumário Executivo - Vendas',
            'data_geracao': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'principais_metricas': [],
            'destaques': [],
            'pontos_atencao': [],
            'recomendacoes': []
        }

        # Extrair métricas principais
        if 'total_vendas' in data:
            summary['principais_metricas'].append({
                'nome': 'Total de Vendas',
                'valor': f"R$ {data['total_vendas']:,.2f}",
                'tipo': 'monetario'
            })

        if 'quantidade_vendas' in data:
            summary['principais_metricas'].append({
                'nome': 'Quantidade de Vendas',
                'valor': str(data['quantidade_vendas']),
                'tipo': 'quantidade'
            })

        if 'ticket_medio' in data:
            summary['principais_metricas'].append({
                'nome': 'Ticket Médio',
                'valor': f"R$ {data['ticket_medio']:,.2f}",
                'tipo': 'monetario'
            })

        if 'taxa_conversao' in data:
            taxa = data['taxa_conversao'] * 100
            summary['principais_metricas'].append({
                'nome': 'Taxa de Conversão',
                'valor': f"{taxa:.1f}%",
                'tipo': 'percentual'
            })

        # Gerar destaques
        if 'variacao_mes_anterior' in data:
            var = data['variacao_mes_anterior']
            if var > 10:
                summary['destaques'].append(f"📈 Crescimento de {var:.1f}% em relação ao mês anterior")
            elif var > 0:
                summary['destaques'].append(f"✅ Crescimento moderado de {var:.1f}%")

        if 'melhor_produto' in data:
            summary['destaques'].append(f"🏆 Produto destaque: {data['melhor_produto']}")

        # Pontos de atenção
        if 'pipeline' in data and data['pipeline'] < 100000:
            summary['pontos_atencao'].append("⚠️ Pipeline abaixo do ideal - necessária ação de prospecção")

        if 'taxa_conversao' in data and data['taxa_conversao'] < 0.15:
            summary['pontos_atencao'].append("⚠️ Taxa de conversão baixa - revisar qualificação de leads")

        # Recomendações
        summary['recomendacoes'].append("Manter acompanhamento semanal das métricas de vendas")
        summary['recomendacoes'].append("Implementar ações para melhorar conversão do pipeline")

        return summary

    def _summarize_financial(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Sumário financeiro"""
        summary = {
            'titulo': 'Sumário Executivo - Financeiro',
            'data_geracao': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'principais_metricas': [],
            'destaques': [],
            'pontos_atencao': [],
            'recomendacoes': []
        }

        # Métricas principais
        if 'receita_total' in data:
            summary['principais_metricas'].append({
                'nome': 'Receita Total',
                'valor': f"R$ {data['receita_total']:,.2f}",
                'tipo': 'monetario'
            })

        if 'despesas_total' in data:
            summary['principais_metricas'].append({
                'nome': 'Despesas Totais',
                'valor': f"R$ {data['despesas_total']:,.2f}",
                'tipo': 'monetario'
            })

        if 'lucro_liquido' in data:
            summary['principais_metricas'].append({
                'nome': 'Lucro Líquido',
                'valor': f"R$ {data['lucro_liquido']:,.2f}",
                'tipo': 'monetario'
            })

        if 'margem_lucro' in data:
            margem = data['margem_lucro'] * 100
            summary['principais_metricas'].append({
                'nome': 'Margem de Lucro',
                'valor': f"{margem:.1f}%",
                'tipo': 'percentual'
            })

        # Destaques e alertas
        if 'contas_receber' in data and 'contas_pagar' in data:
            saldo = data['contas_receber'] - data['contas_pagar']
            if saldo > 0:
                summary['destaques'].append(f"💰 Saldo positivo de R$ {saldo:,.2f}")
            else:
                summary['pontos_atencao'].append(f"⚠️ Saldo negativo de R$ {abs(saldo):,.2f}")

        if 'inadimplencia' in data and data['inadimplencia'] > 5:
            summary['pontos_atencao'].append(f"⚠️ Inadimplência em {data['inadimplencia']:.1f}%")

        # Recomendações
        summary['recomendacoes'].append("Monitorar fluxo de caixa semanalmente")
        summary['recomendacoes'].append("Revisar contratos com margem abaixo do esperado")

        return summary

    def _summarize_customers(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Sumário de clientes"""
        summary = {
            'titulo': 'Sumário Executivo - Clientes',
            'data_geracao': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'principais_metricas': [],
            'destaques': [],
            'pontos_atencao': [],
            'recomendacoes': []
        }

        # Métricas principais
        if 'total_clientes' in data:
            summary['principais_metricas'].append({
                'nome': 'Total de Clientes',
                'valor': str(data['total_clientes']),
                'tipo': 'quantidade'
            })

        if 'novos_clientes' in data:
            summary['principais_metricas'].append({
                'nome': 'Novos Clientes',
                'valor': str(data['novos_clientes']),
                'tipo': 'quantidade'
            })

        if 'churn_rate' in data:
            churn = data['churn_rate'] * 100
            summary['principais_metricas'].append({
                'nome': 'Taxa de Churn',
                'valor': f"{churn:.1f}%",
                'tipo': 'percentual'
            })

        if 'ltv_medio' in data:
            summary['principais_metricas'].append({
                'nome': 'LTV Médio',
                'valor': f"R$ {data['ltv_medio']:,.2f}",
                'tipo': 'monetario'
            })

        # Destaques
        if 'novos_clientes' in data and data['novos_clientes'] > 50:
            summary['destaques'].append(f"🎯 Excelente captação: {data['novos_clientes']} novos clientes")

        # Alertas
        if 'churn_rate' in data and data['churn_rate'] > 0.05:
            summary['pontos_atencao'].append(f"⚠️ Taxa de churn elevada: {data['churn_rate']*100:.1f}%")

        # Recomendações
        summary['recomendacoes'].append("Implementar programa de fidelização de clientes")
        summary['recomendacoes'].append("Analisar motivos de churn e criar ações preventivas")

        return summary

    def _summarize_general(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Sumário geral"""
        summary = {
            'titulo': 'Sumário Executivo - Geral',
            'data_geracao': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'principais_metricas': [],
            'destaques': [],
            'observacoes': []
        }

        # Tentar extrair métricas automaticamente
        for key, value in data.items():
            if isinstance(value, (int, float)):
                summary['principais_metricas'].append({
                    'nome': key.replace('_', ' ').title(),
                    'valor': str(value),
                    'tipo': 'numero'
                })

        summary['observacoes'].append("Sumário gerado automaticamente a partir dos dados disponíveis")

        return summary

    def generate_comparison_report(
        self,
        period1_data: Dict[str, Any],
        period2_data: Dict[str, Any],
        period1_label: str = "Período 1",
        period2_label: str = "Período 2"
    ) -> Dict[str, Any]:
        """
        Gera relatório comparativo entre dois períodos

        Args:
            period1_data: Dados do primeiro período
            period2_data: Dados do segundo período
            period1_label: Rótulo do primeiro período
            period2_label: Rótulo do segundo período

        Returns:
            Relatório comparativo estruturado
        """
        report = {
            'titulo': f'Relatório Comparativo: {period1_label} vs {period2_label}',
            'data_geracao': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'comparacoes': [],
            'destaques': [],
            'conclusoes': []
        }

        # Comparar métricas comuns
        common_keys = set(period1_data.keys()) & set(period2_data.keys())

        for key in common_keys:
            val1 = period1_data[key]
            val2 = period2_data[key]

            if isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
                change = ((val2 - val1) / val1 * 100) if val1 != 0 else 0

                report['comparacoes'].append({
                    'metrica': key.replace('_', ' ').title(),
                    period1_label: val1,
                    period2_label: val2,
                    'variacao_percentual': round(change, 2),
                    'tendencia': 'crescimento' if change > 0 else 'queda' if change < 0 else 'estável'
                })

                # Adicionar destaques
                if abs(change) > 20:
                    direction = "aumento" if change > 0 else "redução"
                    report['destaques'].append(
                        f"{'📈' if change > 0 else '📉'} {key.replace('_', ' ').title()}: "
                        f"{direction} de {abs(change):.1f}%"
                    )

        # Conclusões
        positive_changes = sum(1 for c in report['comparacoes'] if c['variacao_percentual'] > 0)
        negative_changes = sum(1 for c in report['comparacoes'] if c['variacao_percentual'] < 0)

        if positive_changes > negative_changes:
            report['conclusoes'].append(
                f"Performance geral positiva com {positive_changes} métricas em crescimento"
            )
        elif negative_changes > positive_changes:
            report['conclusoes'].append(
                f"Atenção necessária: {negative_changes} métricas em queda"
            )
        else:
            report['conclusoes'].append("Performance estável entre os períodos comparados")

        return report

    def format_summary_as_text(self, summary: Dict[str, Any]) -> str:
        """
        Formata sumário como texto legível

        Args:
            summary: Sumário estruturado

        Returns:
            Texto formatado
        """
        lines = []

        # Título
        lines.append("=" * 60)
        lines.append(summary.get('titulo', 'Sumário Executivo'))
        lines.append("=" * 60)
        lines.append(f"Gerado em: {summary.get('data_geracao', 'N/A')}")
        lines.append("")

        # Principais métricas
        if 'principais_metricas' in summary and summary['principais_metricas']:
            lines.append("📊 PRINCIPAIS MÉTRICAS")
            lines.append("-" * 60)
            for metrica in summary['principais_metricas']:
                lines.append(f"  • {metrica['nome']}: {metrica['valor']}")
            lines.append("")

        # Destaques
        if 'destaques' in summary and summary['destaques']:
            lines.append("✨ DESTAQUES")
            lines.append("-" * 60)
            for destaque in summary['destaques']:
                lines.append(f"  {destaque}")
            lines.append("")

        # Pontos de atenção
        if 'pontos_atencao' in summary and summary['pontos_atencao']:
            lines.append("⚠️  PONTOS DE ATENÇÃO")
            lines.append("-" * 60)
            for ponto in summary['pontos_atencao']:
                lines.append(f"  {ponto}")
            lines.append("")

        # Recomendações
        if 'recomendacoes' in summary and summary['recomendacoes']:
            lines.append("💡 RECOMENDAÇÕES")
            lines.append("-" * 60)
            for rec in summary['recomendacoes']:
                lines.append(f"  • {rec}")
            lines.append("")

        # Comparações (para relatórios comparativos)
        if 'comparacoes' in summary and summary['comparacoes']:
            lines.append("📈 COMPARAÇÕES")
            lines.append("-" * 60)
            for comp in summary['comparacoes'][:5]:  # Mostrar apenas top 5
                metrica = comp['metrica']
                var = comp['variacao_percentual']
                trend_icon = "🔺" if var > 0 else "🔻" if var < 0 else "➡️"
                lines.append(f"  {trend_icon} {metrica}: {var:+.1f}%")
            lines.append("")

        lines.append("=" * 60)

        return "\n".join(lines)


# Instância global
report_summarizer = ReportSummarizer()
