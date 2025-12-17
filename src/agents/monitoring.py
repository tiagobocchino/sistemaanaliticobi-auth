"""
Sistema de Audit Logging e Monitoramento
"""
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from uuid import UUID
import os
from pathlib import Path


class AuditLogger:
    """Sistema de auditoria para operações sensíveis"""

    # Tipos de eventos
    EVENT_API_CALL = "api_call"
    EVENT_DATA_ACCESS = "data_access"
    EVENT_AGENT_QUERY = "agent_query"
    EVENT_TOOL_USE = "tool_use"
    EVENT_ERROR = "error"
    EVENT_SECURITY = "security"

    # Níveis de severidade
    SEVERITY_INFO = "INFO"
    SEVERITY_WARNING = "WARNING"
    SEVERITY_ERROR = "ERROR"
    SEVERITY_CRITICAL = "CRITICAL"

    def __init__(self, log_dir: str = "logs/audit"):
        """
        Args:
            log_dir: Diretório para armazenar logs de auditoria
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Configurar logger
        self.logger = logging.getLogger("audit")
        self.logger.setLevel(logging.INFO)

        # Handler para arquivo diário
        self._setup_file_handler()

        # Handler para console (opcional)
        if os.getenv("AUDIT_LOG_CONSOLE", "false").lower() == "true":
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(self._get_formatter())
            self.logger.addHandler(console_handler)

    def _setup_file_handler(self):
        """Configura handler de arquivo com rotação diária"""
        from logging.handlers import TimedRotatingFileHandler

        log_file = self.log_dir / "audit.log"
        file_handler = TimedRotatingFileHandler(
            log_file,
            when="midnight",
            interval=1,
            backupCount=30,  # Manter 30 dias de logs
            encoding="utf-8"
        )
        file_handler.setFormatter(self._get_formatter())
        self.logger.addHandler(file_handler)

    def _get_formatter(self):
        """Retorna formatter JSON para logs"""
        return logging.Formatter(
            '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "event": %(message)s}'
        )

    def log_event(
        self,
        event_type: str,
        user_id: Optional[str] = None,
        action: str = "",
        details: Optional[Dict[str, Any]] = None,
        severity: str = SEVERITY_INFO,
        ip_address: Optional[str] = None
    ) -> None:
        """
        Registra evento de auditoria

        Args:
            event_type: Tipo do evento (API_CALL, DATA_ACCESS, etc)
            user_id: ID do usuário
            action: Descrição da ação
            details: Detalhes adicionais
            severity: Nível de severidade
            ip_address: Endereço IP (se disponível)
        """
        event_data = {
            "event_type": event_type,
            "user_id": user_id,
            "action": action,
            "details": details or {},
            "severity": severity,
            "ip_address": ip_address,
            "timestamp": datetime.now().isoformat()
        }

        log_message = json.dumps(event_data, ensure_ascii=False)

        if severity == self.SEVERITY_CRITICAL or severity == self.SEVERITY_ERROR:
            self.logger.error(log_message)
        elif severity == self.SEVERITY_WARNING:
            self.logger.warning(log_message)
        else:
            self.logger.info(log_message)

    def log_api_call(
        self,
        user_id: str,
        api_name: str,
        endpoint: str,
        params: Optional[Dict] = None,
        response_status: str = "success",
        duration_ms: Optional[float] = None
    ) -> None:
        """Registra chamada de API"""
        self.log_event(
            event_type=self.EVENT_API_CALL,
            user_id=user_id,
            action=f"API call to {api_name}",
            details={
                "api": api_name,
                "endpoint": endpoint,
                "params": params or {},
                "status": response_status,
                "duration_ms": duration_ms
            }
        )

    def log_data_access(
        self,
        user_id: str,
        table_name: str,
        operation: str,
        filters: Optional[Dict] = None,
        record_count: Optional[int] = None
    ) -> None:
        """Registra acesso a dados"""
        self.log_event(
            event_type=self.EVENT_DATA_ACCESS,
            user_id=user_id,
            action=f"{operation} on {table_name}",
            details={
                "table": table_name,
                "operation": operation,
                "filters": filters or {},
                "record_count": record_count
            }
        )

    def log_agent_query(
        self,
        user_id: str,
        query: str,
        tools_used: List[str],
        response_length: int,
        success: bool = True
    ) -> None:
        """Registra consulta ao agente IA"""
        self.log_event(
            event_type=self.EVENT_AGENT_QUERY,
            user_id=user_id,
            action="Agent query processed",
            details={
                "query": query[:200],  # Limitar tamanho
                "tools_used": tools_used,
                "response_length": response_length,
                "success": success
            }
        )

    def log_security_event(
        self,
        user_id: Optional[str],
        event: str,
        details: Optional[Dict] = None,
        severity: str = SEVERITY_WARNING
    ) -> None:
        """Registra evento de segurança"""
        self.log_event(
            event_type=self.EVENT_SECURITY,
            user_id=user_id,
            action=event,
            details=details or {},
            severity=severity
        )

    def log_error(
        self,
        user_id: Optional[str],
        error_type: str,
        error_message: str,
        stack_trace: Optional[str] = None,
        context: Optional[Dict] = None
    ) -> None:
        """Registra erro"""
        self.log_event(
            event_type=self.EVENT_ERROR,
            user_id=user_id,
            action=f"Error: {error_type}",
            details={
                "error_type": error_type,
                "message": error_message,
                "stack_trace": stack_trace,
                "context": context or {}
            },
            severity=self.SEVERITY_ERROR
        )


class PerformanceMonitor:
    """Monitor de performance e métricas do sistema"""

    def __init__(self):
        self.metrics: Dict[str, List[float]] = {}
        self.counters: Dict[str, int] = {}

    def record_metric(self, metric_name: str, value: float) -> None:
        """
        Registra métrica de performance

        Args:
            metric_name: Nome da métrica (ex: "api_response_time")
            value: Valor da métrica
        """
        if metric_name not in self.metrics:
            self.metrics[metric_name] = []

        self.metrics[metric_name].append(value)

        # Manter apenas últimas 1000 medições
        if len(self.metrics[metric_name]) > 1000:
            self.metrics[metric_name] = self.metrics[metric_name][-1000:]

    def increment_counter(self, counter_name: str, amount: int = 1) -> None:
        """
        Incrementa contador

        Args:
            counter_name: Nome do contador (ex: "total_api_calls")
            amount: Quantidade a incrementar
        """
        if counter_name not in self.counters:
            self.counters[counter_name] = 0

        self.counters[counter_name] += amount

    def get_metric_stats(self, metric_name: str) -> Dict[str, float]:
        """
        Retorna estatísticas de uma métrica

        Args:
            metric_name: Nome da métrica

        Returns:
            Dict com min, max, avg, p95, p99
        """
        if metric_name not in self.metrics or not self.metrics[metric_name]:
            return {
                "min": 0,
                "max": 0,
                "avg": 0,
                "p95": 0,
                "p99": 0,
                "count": 0
            }

        values = sorted(self.metrics[metric_name])
        count = len(values)

        return {
            "min": values[0],
            "max": values[-1],
            "avg": sum(values) / count,
            "p95": values[int(count * 0.95)] if count > 0 else 0,
            "p99": values[int(count * 0.99)] if count > 0 else 0,
            "count": count
        }

    def get_all_metrics(self) -> Dict[str, Any]:
        """Retorna todas as métricas e contadores"""
        metrics_summary = {}
        for metric_name in self.metrics:
            metrics_summary[metric_name] = self.get_metric_stats(metric_name)

        return {
            "metrics": metrics_summary,
            "counters": self.counters.copy(),
            "timestamp": datetime.now().isoformat()
        }

    def reset_metrics(self) -> None:
        """Reseta todas as métricas"""
        self.metrics.clear()
        self.counters.clear()


class UsageTracker:
    """Rastreador de uso de APIs externas e recursos"""

    def __init__(self):
        self.usage: Dict[str, Dict[str, Any]] = {}

    def track_api_usage(
        self,
        api_name: str,
        endpoint: str,
        user_id: str,
        response_size: Optional[int] = None,
        cost: Optional[float] = None
    ) -> None:
        """
        Rastreia uso de API externa

        Args:
            api_name: Nome da API (Sienge, CVDW, OpenAI, etc)
            endpoint: Endpoint chamado
            user_id: ID do usuário
            response_size: Tamanho da resposta em bytes
            cost: Custo estimado da chamada
        """
        key = f"{api_name}:{endpoint}"

        if key not in self.usage:
            self.usage[key] = {
                "api": api_name,
                "endpoint": endpoint,
                "total_calls": 0,
                "total_size": 0,
                "total_cost": 0.0,
                "users": set(),
                "first_call": datetime.now().isoformat(),
                "last_call": None
            }

        self.usage[key]["total_calls"] += 1
        if response_size:
            self.usage[key]["total_size"] += response_size
        if cost:
            self.usage[key]["total_cost"] += cost
        self.usage[key]["users"].add(user_id)
        self.usage[key]["last_call"] = datetime.now().isoformat()

    def get_usage_report(self, api_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Gera relatório de uso

        Args:
            api_name: Filtrar por API específica (opcional)

        Returns:
            Relatório de uso
        """
        filtered_usage = {}

        for key, data in self.usage.items():
            if api_name is None or data["api"] == api_name:
                # Converter set para list para JSON
                usage_data = data.copy()
                usage_data["unique_users"] = len(usage_data["users"])
                del usage_data["users"]
                filtered_usage[key] = usage_data

        # Calcular totais
        total_calls = sum(u["total_calls"] for u in filtered_usage.values())
        total_cost = sum(u["total_cost"] for u in filtered_usage.values())
        total_size = sum(u["total_size"] for u in filtered_usage.values())

        return {
            "usage_by_endpoint": filtered_usage,
            "totals": {
                "total_calls": total_calls,
                "total_cost": total_cost,
                "total_size_bytes": total_size,
                "total_size_mb": total_size / (1024 * 1024)
            },
            "generated_at": datetime.now().isoformat()
        }

    def check_rate_limit(
        self,
        api_name: str,
        user_id: str,
        max_calls_per_hour: int = 100
    ) -> Dict[str, Any]:
        """
        Verifica se usuário excedeu rate limit

        Args:
            api_name: Nome da API
            user_id: ID do usuário
            max_calls_per_hour: Limite de chamadas por hora

        Returns:
            Dict com status do rate limit
        """
        # Simplificado - em produção usar Redis com TTL
        key = f"{api_name}:rate_limit:{user_id}"

        # Contar chamadas da última hora (simplificado)
        recent_calls = 0
        for usage_key, data in self.usage.items():
            if api_name in usage_key and user_id in data.get("users", set()):
                recent_calls += data["total_calls"]

        exceeded = recent_calls >= max_calls_per_hour

        return {
            "user_id": user_id,
            "api": api_name,
            "calls_this_hour": recent_calls,
            "limit": max_calls_per_hour,
            "exceeded": exceeded,
            "remaining": max(0, max_calls_per_hour - recent_calls)
        }


# Instâncias globais
audit_logger = AuditLogger()
performance_monitor = PerformanceMonitor()
usage_tracker = UsageTracker()
