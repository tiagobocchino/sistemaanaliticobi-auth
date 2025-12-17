"""
Gerador de Alertas e Identificador de Anomalias
"""
from typing import Dict, List, Any, Optional
import pandas as pd
from datetime import datetime, timedelta
import json


class AlertGenerator:
    """Identifica anomalias e gera alertas automáticos"""

    # Tipos de alerta
    ALERT_CRITICAL = "CRÍTICO"
    ALERT_WARNING = "ATENÇÃO"
    ALERT_INFO = "INFORMATIVO"

    def analyze_anomalies(
        self,
        data: List[Dict],
        date_column: str = 'data',
        value_column: str = 'valor',
        threshold_std: float = 2.0
    ) -> Dict[str, Any]:
        """
        Identifica anomalias usando análise estatística

        Args:
            data: Dados para análise
            date_column: Coluna de data
            value_column: Coluna de valor
            threshold_std: Quantos desvios padrão considerar como anomalia (padrão: 2.0)

        Returns:
            Relatório de anomalias detectadas
        """
        if not data or len(data) < 10:
            return {
                "erro": "Dados insuficientes (mínimo 10 registros)",
                "anomalias": []
            }

        try:
            df = pd.DataFrame(data)
            df[date_column] = pd.to_datetime(df[date_column])
            df = df.sort_values(date_column)

            # Calcular estatísticas
            mean = df[value_column].mean()
            std = df[value_column].std()
            median = df[value_column].median()

            # Identificar anomalias (valores fora de N desvios padrão)
            df['z_score'] = (df[value_column] - mean) / std
            anomalies = df[abs(df['z_score']) > threshold_std]

            anomaly_list = []
            for _, row in anomalies.iterrows():
                severity = self._determine_severity(abs(row['z_score']), threshold_std)
                anomaly_list.append({
                    'data': row[date_column].strftime('%Y-%m-%d'),
                    'valor': float(row[value_column]),
                    'z_score': round(float(row['z_score']), 2),
                    'desvio_percentual': round(((row[value_column] - mean) / mean * 100), 2),
                    'severidade': severity
                })

            return {
                'total_anomalias': len(anomaly_list),
                'anomalias': anomaly_list,
                'estatisticas': {
                    'media': round(float(mean), 2),
                    'mediana': round(float(median), 2),
                    'desvio_padrao': round(float(std), 2),
                    'minimo': round(float(df[value_column].min()), 2),
                    'maximo': round(float(df[value_column].max()), 2)
                },
                'insights': self._generate_anomaly_insights(anomaly_list, mean, std)
            }
        except Exception as e:
            return {"erro": f"Erro ao analisar anomalias: {str(e)}"}

    def _determine_severity(self, z_score: float, threshold: float) -> str:
        """Determina severidade da anomalia"""
        if z_score > threshold * 1.5:
            return self.ALERT_CRITICAL
        elif z_score > threshold:
            return self.ALERT_WARNING
        else:
            return self.ALERT_INFO

    def _generate_anomaly_insights(
        self,
        anomalies: List[Dict],
        mean: float,
        std: float
    ) -> List[str]:
        """Gera insights sobre anomalias detectadas"""
        insights = []

        if not anomalies:
            insights.append("Nenhuma anomalia significativa detectada no período")
            insights.append("Dados dentro dos padrões esperados")
            return insights

        # Contar por severidade
        critical = sum(1 for a in anomalies if a['severidade'] == self.ALERT_CRITICAL)
        warnings = sum(1 for a in anomalies if a['severidade'] == self.ALERT_WARNING)

        if critical > 0:
            insights.append(f"⚠️ {critical} anomalia(s) crítica(s) detectada(s) - requer atenção imediata")

        if warnings > 0:
            insights.append(f"⚡ {warnings} anomalia(s) de atenção detectada(s)")

        # Analisar padrão das anomalias
        positive_anomalies = [a for a in anomalies if a['desvio_percentual'] > 0]
        negative_anomalies = [a for a in anomalies if a['desvio_percentual'] < 0]

        if len(positive_anomalies) > len(negative_anomalies):
            insights.append("Maioria das anomalias são valores acima da média (picos de performance)")
        elif len(negative_anomalies) > len(positive_anomalies):
            insights.append("Maioria das anomalias são valores abaixo da média (quedas de performance)")

        insights.append("Recomendação: Investigar causas das anomalias detectadas")

        return insights

    def generate_performance_alerts(
        self,
        current_data: Dict[str, Any],
        historical_data: List[Dict],
        thresholds: Optional[Dict[str, float]] = None
    ) -> List[Dict[str, Any]]:
        """
        Gera alertas de performance baseados em thresholds

        Args:
            current_data: Dados atuais a serem comparados
            historical_data: Dados históricos para baseline
            thresholds: Thresholds personalizados (opcional)

        Returns:
            Lista de alertas gerados
        """
        if thresholds is None:
            thresholds = {
                'vendas_queda': -15.0,  # Alerta se vendas caírem mais de 15%
                'vendas_pico': 30.0,     # Alerta se vendas subirem mais de 30%
                'conversao_baixa': 10.0, # Alerta se conversão cair abaixo de 10%
                'pipeline_critico': 50000.0  # Alerta se pipeline cair abaixo deste valor
            }

        alerts = []

        try:
            # Calcular baseline do histórico
            if historical_data:
                df = pd.DataFrame(historical_data)
                historical_avg = {col: df[col].mean() for col in df.select_dtypes(include=['number']).columns}
            else:
                historical_avg = {}

            # Verificar vendas
            if 'vendas' in current_data and 'vendas' in historical_avg:
                current_sales = current_data['vendas']
                avg_sales = historical_avg['vendas']
                change = ((current_sales - avg_sales) / avg_sales * 100) if avg_sales != 0 else 0

                if change < thresholds['vendas_queda']:
                    alerts.append({
                        'tipo': 'VENDAS',
                        'severidade': self.ALERT_CRITICAL,
                        'titulo': 'Queda Significativa em Vendas',
                        'mensagem': f"Vendas caíram {abs(change):.1f}% em relação à média histórica",
                        'valor_atual': current_sales,
                        'valor_esperado': avg_sales,
                        'acao_recomendada': 'Revisar estratégias de vendas e marketing imediatamente'
                    })
                elif change > thresholds['vendas_pico']:
                    alerts.append({
                        'tipo': 'VENDAS',
                        'severidade': self.ALERT_INFO,
                        'titulo': 'Pico de Vendas Detectado',
                        'mensagem': f"Vendas subiram {change:.1f}% acima da média",
                        'valor_atual': current_sales,
                        'valor_esperado': avg_sales,
                        'acao_recomendada': 'Analisar fatores de sucesso e replicar estratégias'
                    })

            # Verificar taxa de conversão
            if 'taxa_conversao' in current_data:
                conv_rate = current_data['taxa_conversao'] * 100

                if conv_rate < thresholds['conversao_baixa']:
                    alerts.append({
                        'tipo': 'CONVERSÃO',
                        'severidade': self.ALERT_WARNING,
                        'titulo': 'Taxa de Conversão Baixa',
                        'mensagem': f"Conversão de apenas {conv_rate:.1f}%",
                        'valor_atual': conv_rate,
                        'acao_recomendada': 'Otimizar funil de vendas e qualificação de leads'
                    })

            # Verificar pipeline
            if 'pipeline' in current_data:
                pipeline = current_data['pipeline']

                if pipeline < thresholds['pipeline_critico']:
                    alerts.append({
                        'tipo': 'PIPELINE',
                        'severidade': self.ALERT_CRITICAL,
                        'titulo': 'Pipeline Crítico',
                        'mensagem': f"Pipeline em R$ {pipeline:,.2f} abaixo do mínimo saudável",
                        'valor_atual': pipeline,
                        'valor_minimo': thresholds['pipeline_critico'],
                        'acao_recomendada': 'Intensificar prospecção e geração de leads'
                    })

            # Verificar inadimplência (se disponível)
            if 'inadimplencia' in current_data:
                inadimplencia_pct = current_data['inadimplencia']

                if inadimplencia_pct > 5.0:
                    alerts.append({
                        'tipo': 'FINANCEIRO',
                        'severidade': self.ALERT_WARNING,
                        'titulo': 'Inadimplência Elevada',
                        'mensagem': f"Taxa de inadimplência em {inadimplencia_pct:.1f}%",
                        'valor_atual': inadimplencia_pct,
                        'acao_recomendada': 'Revisar política de crédito e cobranças'
                    })

        except Exception as e:
            alerts.append({
                'tipo': 'SISTEMA',
                'severidade': self.ALERT_WARNING,
                'titulo': 'Erro ao Gerar Alertas',
                'mensagem': f"Erro: {str(e)}",
                'acao_recomendada': 'Verificar dados de entrada'
            })

        return alerts

    def check_threshold_breach(
        self,
        metric_name: str,
        current_value: float,
        threshold: float,
        comparison: str = 'below'
    ) -> Optional[Dict[str, Any]]:
        """
        Verifica se métrica ultrapassou threshold

        Args:
            metric_name: Nome da métrica
            current_value: Valor atual
            threshold: Threshold de comparação
            comparison: 'below', 'above', ou 'equal'

        Returns:
            Alerta se threshold foi ultrapassado, None caso contrário
        """
        breached = False

        if comparison == 'below' and current_value < threshold:
            breached = True
            msg = f"{metric_name} está abaixo do threshold ({current_value:.2f} < {threshold:.2f})"
        elif comparison == 'above' and current_value > threshold:
            breached = True
            msg = f"{metric_name} está acima do threshold ({current_value:.2f} > {threshold:.2f})"
        elif comparison == 'equal' and abs(current_value - threshold) < 0.01:
            breached = True
            msg = f"{metric_name} atingiu exatamente o threshold ({current_value:.2f})"

        if breached:
            return {
                'metrica': metric_name,
                'valor_atual': current_value,
                'threshold': threshold,
                'tipo_comparacao': comparison,
                'mensagem': msg,
                'timestamp': datetime.now().isoformat()
            }

        return None


# Instância global
alert_generator = AlertGenerator()
