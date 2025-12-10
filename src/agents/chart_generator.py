"""
Gerador de Gráficos e Visualizações
Cria gráficos usando matplotlib e plotly baseado nos dados de análise
"""
import io
import base64
from typing import Dict, List, Any, Optional, Literal
from dataclasses import dataclass
import matplotlib
matplotlib.use('Agg')  # Backend não-interativo para servidor
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime


ChartType = Literal["bar", "line", "pie", "scatter", "area", "table"]


@dataclass
class ChartData:
    """Dados para geração de um gráfico"""
    title: str
    chart_type: ChartType
    data: Dict[str, Any]
    labels: Optional[List[str]] = None
    values: Optional[List[float]] = None
    x_label: Optional[str] = None
    y_label: Optional[str] = None
    colors: Optional[List[str]] = None


@dataclass
class GeneratedChart:
    """Gráfico gerado"""
    title: str
    chart_type: str
    format: Literal["matplotlib", "plotly"]
    image_base64: Optional[str] = None  # Para matplotlib
    plotly_json: Optional[Dict] = None  # Para plotly
    html: Optional[str] = None
    description: str = ""


class ChartGenerator:
    """
    Gerador inteligente de gráficos baseado nos dados
    """

    def __init__(self):
        # Paleta de cores padrão
        self.default_colors = [
            '#2E86AB', '#A23B72', '#F18F01', '#C73E1D',
            '#6A994E', '#BC4B51', '#8B5A3C', '#5E5E5E'
        ]

    def generate_charts_from_analysis(
        self,
        intent: str,
        data: Dict[str, Any]
    ) -> List[GeneratedChart]:
        """
        Gera gráficos automaticamente baseado na intenção e dados

        Args:
            intent: Intenção da análise (vendas, financeiro, etc)
            data: Dados retornados das APIs

        Returns:
            Lista de gráficos gerados
        """
        charts = []

        # Gerar gráficos específicos por intenção
        if intent == "financeiro":
            charts.extend(self._generate_financial_charts(data))
        elif intent == "vendas":
            charts.extend(self._generate_sales_charts(data))
        elif intent == "clientes":
            charts.extend(self._generate_client_charts(data))
        elif intent == "comparacao":
            charts.extend(self._generate_comparison_charts(data))
        else:
            # Gráfico genérico
            charts.extend(self._generate_generic_charts(data))

        return charts

    def _generate_financial_charts(self, data: Dict[str, Any]) -> List[GeneratedChart]:
        """Gera gráficos financeiros"""
        charts = []

        # Procurar dados de contas a pagar/receber
        sienge_data = data.get("sienge", {})

        if "contas_pagar" in sienge_data and "contas_receber" in sienge_data:
            cp = sienge_data["contas_pagar"]
            cr = sienge_data["contas_receber"]

            # Gráfico de barras: Contas a Pagar vs Contas a Receber
            if isinstance(cp, dict) and isinstance(cr, dict):
                chart_data = ChartData(
                    title="Contas a Pagar vs Contas a Receber",
                    chart_type="bar",
                    data={
                        "categories": ["A Pagar", "A Receber"],
                        "values": [
                            cp.get("total", 0),
                            cr.get("total", 0)
                        ]
                    },
                    y_label="Valor (R$)"
                )
                charts.append(self._create_bar_chart(chart_data))

            # Gráfico de pizza: Distribuição de contas
            if isinstance(cp, dict) and isinstance(cr, dict):
                chart_data = ChartData(
                    title="Distribuição de Contas",
                    chart_type="pie",
                    data={},
                    labels=["Contas a Pagar", "Contas a Receber"],
                    values=[
                        cp.get("quantidade", 0),
                        cr.get("quantidade", 0)
                    ]
                )
                charts.append(self._create_pie_chart(chart_data))

        return charts

    def _generate_sales_charts(self, data: Dict[str, Any]) -> List[GeneratedChart]:
        """Gera gráficos de vendas"""
        charts = []

        cvdw_data = data.get("cvdw", {})

        # Gráfico de funil de vendas
        if "oportunidades_abertas" in cvdw_data:
            chart_data = ChartData(
                title="Pipeline de Vendas",
                chart_type="bar",
                data={
                    "categories": ["Oportunidades", "Valor Estimado (milhares)"],
                    "values": [
                        cvdw_data.get("oportunidades_abertas", 0),
                        cvdw_data.get("valor_pipeline", 0) / 1000
                    ]
                },
                y_label="Quantidade / Valor"
            )
            charts.append(self._create_bar_chart(chart_data))

        # Taxa de conversão
        if "taxa_conversao" in cvdw_data:
            taxa = cvdw_data.get("taxa_conversao", 0) * 100
            chart_data = ChartData(
                title="Taxa de Conversão",
                chart_type="pie",
                data={},
                labels=["Convertido", "Não Convertido"],
                values=[taxa, 100 - taxa]
            )
            charts.append(self._create_pie_chart(chart_data))

        return charts

    def _generate_client_charts(self, data: Dict[str, Any]) -> List[GeneratedChart]:
        """Gera gráficos de clientes"""
        charts = []

        cvdw_data = data.get("cvdw", {})

        if "total_clientes" in cvdw_data:
            chart_data = ChartData(
                title="Estatísticas de Clientes",
                chart_type="bar",
                data={
                    "categories": ["Total", "Novos (mês)", "Ativos"],
                    "values": [
                        cvdw_data.get("total_clientes", 0),
                        cvdw_data.get("novos_clientes_mes", 0),
                        cvdw_data.get("clientes_ativos", 0)
                    ]
                },
                y_label="Quantidade"
            )
            charts.append(self._create_bar_chart(chart_data))

        return charts

    def _generate_comparison_charts(self, data: Dict[str, Any]) -> List[GeneratedChart]:
        """Gera gráficos de comparação entre fontes"""
        charts = []

        # Comparar dados de diferentes fontes
        sources = list(data.keys())
        if len(sources) >= 2:
            # Criar gráfico comparativo
            pass

        return charts

    def _generate_generic_charts(self, data: Dict[str, Any]) -> List[GeneratedChart]:
        """Gera gráficos genéricos baseado nos dados disponíveis"""
        charts = []

        # Iterar sobre as fontes de dados
        for source_name, source_data in data.items():
            if isinstance(source_data, dict):
                # Procurar por valores numéricos
                numeric_data = {k: v for k, v in source_data.items()
                                if isinstance(v, (int, float)) and k != "fonte"}

                if len(numeric_data) > 0:
                    chart_data = ChartData(
                        title=f"Dados de {source_name.upper()}",
                        chart_type="bar",
                        data={
                            "categories": list(numeric_data.keys()),
                            "values": list(numeric_data.values())
                        }
                    )
                    charts.append(self._create_bar_chart(chart_data))

        return charts

    def _create_bar_chart(self, chart_data: ChartData) -> GeneratedChart:
        """Cria gráfico de barras usando plotly"""
        try:
            categories = chart_data.data.get("categories", [])
            values = chart_data.data.get("values", [])

            fig = go.Figure(data=[
                go.Bar(
                    x=categories,
                    y=values,
                    marker_color=self.default_colors[0],
                    text=values,
                    textposition='auto',
                )
            ])

            fig.update_layout(
                title=chart_data.title,
                xaxis_title=chart_data.x_label or "",
                yaxis_title=chart_data.y_label or "",
                height=400,
                showlegend=False,
                template="plotly_white"
            )

            return GeneratedChart(
                title=chart_data.title,
                chart_type="bar",
                format="plotly",
                plotly_json=fig.to_dict(),
                html=fig.to_html(include_plotlyjs='cdn'),
                description=f"Gráfico de barras mostrando {chart_data.title.lower()}"
            )

        except Exception as e:
            return self._create_error_chart(f"Erro ao criar gráfico: {str(e)}")

    def _create_line_chart(self, chart_data: ChartData) -> GeneratedChart:
        """Cria gráfico de linhas usando plotly"""
        try:
            x_data = chart_data.data.get("x", [])
            y_data = chart_data.data.get("y", [])

            fig = go.Figure(data=[
                go.Scatter(
                    x=x_data,
                    y=y_data,
                    mode='lines+markers',
                    line=dict(color=self.default_colors[0], width=2),
                    marker=dict(size=8)
                )
            ])

            fig.update_layout(
                title=chart_data.title,
                xaxis_title=chart_data.x_label or "",
                yaxis_title=chart_data.y_label or "",
                height=400,
                template="plotly_white"
            )

            return GeneratedChart(
                title=chart_data.title,
                chart_type="line",
                format="plotly",
                plotly_json=fig.to_dict(),
                html=fig.to_html(include_plotlyjs='cdn'),
                description=f"Gráfico de linhas mostrando {chart_data.title.lower()}"
            )

        except Exception as e:
            return self._create_error_chart(f"Erro ao criar gráfico: {str(e)}")

    def _create_pie_chart(self, chart_data: ChartData) -> GeneratedChart:
        """Cria gráfico de pizza usando plotly"""
        try:
            labels = chart_data.labels or []
            values = chart_data.values or []

            fig = go.Figure(data=[
                go.Pie(
                    labels=labels,
                    values=values,
                    marker=dict(colors=self.default_colors[:len(labels)]),
                    textinfo='label+percent',
                    hovertemplate='<b>%{label}</b><br>Valor: %{value}<br>Percentual: %{percent}<extra></extra>'
                )
            ])

            fig.update_layout(
                title=chart_data.title,
                height=400,
                template="plotly_white"
            )

            return GeneratedChart(
                title=chart_data.title,
                chart_type="pie",
                format="plotly",
                plotly_json=fig.to_dict(),
                html=fig.to_html(include_plotlyjs='cdn'),
                description=f"Gráfico de pizza mostrando {chart_data.title.lower()}"
            )

        except Exception as e:
            return self._create_error_chart(f"Erro ao criar gráfico: {str(e)}")

    def _create_table_chart(self, chart_data: ChartData) -> GeneratedChart:
        """Cria tabela usando plotly"""
        try:
            df = pd.DataFrame(chart_data.data)

            fig = go.Figure(data=[
                go.Table(
                    header=dict(
                        values=list(df.columns),
                        fill_color=self.default_colors[0],
                        font=dict(color='white', size=12),
                        align='left'
                    ),
                    cells=dict(
                        values=[df[col] for col in df.columns],
                        fill_color='white',
                        align='left'
                    )
                )
            ])

            fig.update_layout(
                title=chart_data.title,
                height=400
            )

            return GeneratedChart(
                title=chart_data.title,
                chart_type="table",
                format="plotly",
                plotly_json=fig.to_dict(),
                html=fig.to_html(include_plotlyjs='cdn'),
                description=f"Tabela mostrando {chart_data.title.lower()}"
            )

        except Exception as e:
            return self._create_error_chart(f"Erro ao criar tabela: {str(e)}")

    def _create_matplotlib_chart(self, chart_data: ChartData) -> GeneratedChart:
        """Cria gráfico usando matplotlib (fallback)"""
        try:
            fig, ax = plt.subplots(figsize=(10, 6))

            if chart_data.chart_type == "bar":
                categories = chart_data.data.get("categories", [])
                values = chart_data.data.get("values", [])
                ax.bar(categories, values, color=self.default_colors[0])
                ax.set_ylabel(chart_data.y_label or "")

            elif chart_data.chart_type == "pie":
                ax.pie(
                    chart_data.values,
                    labels=chart_data.labels,
                    autopct='%1.1f%%',
                    colors=self.default_colors[:len(chart_data.labels)]
                )

            ax.set_title(chart_data.title)
            plt.tight_layout()

            # Converter para base64
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
            plt.close(fig)

            return GeneratedChart(
                title=chart_data.title,
                chart_type=chart_data.chart_type,
                format="matplotlib",
                image_base64=image_base64,
                description=f"Gráfico {chart_data.chart_type} mostrando {chart_data.title.lower()}"
            )

        except Exception as e:
            return self._create_error_chart(f"Erro ao criar gráfico matplotlib: {str(e)}")

    def _create_error_chart(self, error_message: str) -> GeneratedChart:
        """Cria um placeholder para erro"""
        return GeneratedChart(
            title="Erro na Geração do Gráfico",
            chart_type="error",
            format="plotly",
            html=f"<div style='color: red;'>{error_message}</div>",
            description=error_message
        )

    def create_summary_report(
        self,
        title: str,
        charts: List[GeneratedChart],
        text_analysis: str
    ) -> str:
        """
        Cria relatório HTML completo com gráficos e análise

        Args:
            title: Título do relatório
            charts: Lista de gráficos gerados
            text_analysis: Texto da análise

        Returns:
            HTML completo do relatório
        """
        html_parts = [
            f"<html><head><title>{title}</title>",
            "<style>",
            "body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }",
            ".report-container { max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }",
            "h1 { color: #2E86AB; border-bottom: 3px solid #2E86AB; padding-bottom: 10px; }",
            "h2 { color: #333; margin-top: 30px; }",
            ".analysis { background: #f9f9f9; padding: 20px; border-left: 4px solid #2E86AB; margin: 20px 0; }",
            ".chart { margin: 30px 0; }",
            ".chart-title { font-size: 18px; font-weight: bold; color: #333; margin-bottom: 10px; }",
            ".timestamp { color: #666; font-size: 14px; }",
            "</style>",
            "<script src='https://cdn.plot.ly/plotly-latest.min.js'></script>",
            "</head><body>",
            "<div class='report-container'>",
            f"<h1>{title}</h1>",
            f"<p class='timestamp'>Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</p>",
            "<div class='analysis'>",
            "<h2>Análise</h2>",
            f"<pre style='white-space: pre-wrap;'>{text_analysis}</pre>",
            "</div>",
            "<h2>Visualizações</h2>"
        ]

        # Adicionar cada gráfico
        for i, chart in enumerate(charts):
            html_parts.append(f"<div class='chart' id='chart-{i}'>")
            html_parts.append(f"<div class='chart-title'>{chart.title}</div>")

            if chart.format == "plotly" and chart.html:
                html_parts.append(chart.html)
            elif chart.format == "matplotlib" and chart.image_base64:
                html_parts.append(
                    f"<img src='data:image/png;base64,{chart.image_base64}' "
                    f"style='max-width: 100%; height: auto;'/>"
                )

            html_parts.append(f"<p style='color: #666; font-size: 14px;'>{chart.description}</p>")
            html_parts.append("</div>")

        html_parts.extend([
            "</div>",
            "</body></html>"
        ])

        return "\n".join(html_parts)


# Instância global
chart_generator = ChartGenerator()
