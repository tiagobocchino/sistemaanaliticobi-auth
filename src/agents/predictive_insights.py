"""
Gerador de Insights Preditivos baseados em histórico
"""
from typing import Dict, List, Any, Optional
import pandas as pd
from datetime import datetime, timedelta
import json


class PredictiveInsights:
    """Gera previsões simples baseadas em dados históricos"""

    def forecast_sales(
        self,
        data: List[Dict],
        date_column: str = 'data',
        value_column: str = 'valor',
        periods_ahead: int = 3
    ) -> Dict[str, Any]:
        """
        Gera previsão de vendas para próximos períodos

        Args:
            data: Dados históricos
            date_column: Coluna de data
            value_column: Coluna de valor
            periods_ahead: Quantos períodos prever (padrão: 3 meses)

        Returns:
            Previsão com intervalos de confiança
        """
        if not data or len(data) < 3:
            return {
                "erro": "Dados insuficientes para previsão (mínimo 3 registros)",
                "previsao": []
            }

        try:
            df = pd.DataFrame(data)
            df[date_column] = pd.to_datetime(df[date_column])
            df = df.sort_values(date_column)

            # Agrupar por mês
            df['mes'] = df[date_column].dt.to_period('M')
            monthly = df.groupby('mes')[value_column].sum()

            # Usar média móvel e tendência linear
            predictions = self._simple_forecast(monthly.values, periods_ahead)

            # Gerar datas futuras
            last_date = df[date_column].max()
            future_dates = [last_date + timedelta(days=30 * (i + 1)) for i in range(periods_ahead)]

            forecast_data = []
            for i, (pred, lower, upper) in enumerate(predictions):
                forecast_data.append({
                    'periodo': future_dates[i].strftime('%Y-%m'),
                    'previsao': round(pred, 2),
                    'limite_inferior': round(lower, 2),
                    'limite_superior': round(upper, 2),
                    'confianca': '80%'
                })

            # Calcular métricas de qualidade
            historical_avg = float(monthly.mean())
            historical_std = float(monthly.std())

            return {
                'previsoes': forecast_data,
                'metricas_historicas': {
                    'media_mensal': round(historical_avg, 2),
                    'desvio_padrao': round(historical_std, 2),
                    'periodos_analisados': len(monthly)
                },
                'insights': self._generate_forecast_insights(forecast_data, historical_avg)
            }
        except Exception as e:
            return {"erro": f"Erro ao gerar previsão: {str(e)}"}

    def _simple_forecast(
        self,
        values: Any,
        periods: int
    ) -> List[tuple]:
        """
        Previsão simples usando média móvel e tendência linear

        Returns:
            Lista de tuplas (previsão, limite_inferior, limite_superior)
        """
        n = len(values)

        # Calcular tendência
        x = list(range(n))
        y = values

        # Regressão linear simples
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(xi * yi for xi, yi in zip(x, y))
        sum_x2 = sum(xi ** 2 for xi in x)

        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)
        intercept = (sum_y - slope * sum_x) / n

        # Calcular desvio padrão para intervalos de confiança
        predictions_historical = [slope * xi + intercept for xi in x]
        residuals = [y[i] - predictions_historical[i] for i in range(n)]
        std = (sum(r ** 2 for r in residuals) / n) ** 0.5

        # Gerar previsões
        forecasts = []
        for i in range(periods):
            future_x = n + i
            pred = slope * future_x + intercept

            # Intervalo de confiança (aproximadamente 80%)
            margin = 1.28 * std  # 1.28 para ~80% de confiança
            lower = pred - margin
            upper = pred + margin

            forecasts.append((pred, lower, upper))

        return forecasts

    def _generate_forecast_insights(
        self,
        forecasts: List[Dict],
        historical_avg: float
    ) -> List[str]:
        """Gera insights sobre as previsões"""
        insights = []

        if not forecasts:
            return insights

        # Comparar primeira previsão com média histórica
        first_forecast = forecasts[0]['previsao']
        change = ((first_forecast - historical_avg) / historical_avg * 100) if historical_avg != 0 else 0

        if change > 10:
            insights.append(f"Previsão indica crescimento de {change:.1f}% em relação à média histórica")
        elif change < -10:
            insights.append(f"Previsão indica queda de {abs(change):.1f}% em relação à média histórica")
        else:
            insights.append("Previsão indica estabilidade em relação à média histórica")

        # Analisar amplitude dos intervalos
        avg_range = sum((f['limite_superior'] - f['limite_inferior']) for f in forecasts) / len(forecasts)
        uncertainty = (avg_range / first_forecast * 100) if first_forecast != 0 else 0

        if uncertainty > 50:
            insights.append("Alta incerteza nas previsões - dados históricos muito voláteis")
        elif uncertainty < 20:
            insights.append("Baixa incerteza nas previsões - padrão histórico consistente")

        insights.append("Recomendação: Revisar previsões mensalmente com dados reais")

        return insights

    def identify_patterns(
        self,
        data: List[Dict],
        date_column: str = 'data',
        value_column: str = 'valor'
    ) -> Dict[str, Any]:
        """
        Identifica padrões sazonais e cíclicos nos dados

        Args:
            data: Dados históricos
            date_column: Coluna de data
            value_column: Coluna de valor

        Returns:
            Análise de padrões identificados
        """
        if not data or len(data) < 12:
            return {
                "erro": "Dados insuficientes para análise de padrões (mínimo 12 meses)",
                "padroes": []
            }

        try:
            df = pd.DataFrame(data)
            df[date_column] = pd.to_datetime(df[date_column])

            # Análise por mês do ano
            df['mes_ano'] = df[date_column].dt.month
            monthly_pattern = df.groupby('mes_ano')[value_column].mean()

            # Identificar meses de pico e baixa
            best_month = int(monthly_pattern.idxmax())
            worst_month = int(monthly_pattern.idxmin())
            best_value = float(monthly_pattern.max())
            worst_value = float(monthly_pattern.min())

            months_pt = {
                1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
                5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
                9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
            }

            # Análise por dia da semana
            df['dia_semana'] = df[date_column].dt.dayofweek
            weekday_pattern = df.groupby('dia_semana')[value_column].mean()

            dias_pt = {
                0: 'Segunda', 1: 'Terça', 2: 'Quarta',
                3: 'Quinta', 4: 'Sexta', 5: 'Sábado', 6: 'Domingo'
            }

            best_weekday = int(weekday_pattern.idxmax())
            worst_weekday = int(weekday_pattern.idxmin())

            return {
                'sazonalidade_mensal': {
                    'melhor_mes': months_pt[best_month],
                    'valor_medio': round(best_value, 2),
                    'pior_mes': months_pt[worst_month],
                    'valor_medio_pior': round(worst_value, 2),
                    'variacao': round(((best_value - worst_value) / worst_value * 100), 2)
                },
                'padrao_semanal': {
                    'melhor_dia': dias_pt[best_weekday],
                    'pior_dia': dias_pt[worst_weekday]
                },
                'insights': [
                    f"{months_pt[best_month]} historicamente é o melhor mês",
                    f"{months_pt[worst_month]} tende a ter menor performance",
                    f"Variação sazonal de {((best_value - worst_value) / worst_value * 100):.1f}% entre melhor e pior mês",
                    f"Melhor dia da semana: {dias_pt[best_weekday]}"
                ]
            }
        except Exception as e:
            return {"erro": f"Erro ao identificar padrões: {str(e)}"}


# Instância global
predictive_insights = PredictiveInsights()
