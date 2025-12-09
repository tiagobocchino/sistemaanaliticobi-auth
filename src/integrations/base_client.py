"""
Cliente base HTTP para integrações com APIs empresariais
"""
import httpx
import asyncio
from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
import json
import os

from ..config import get_settings


class BaseAPIClient(ABC):
    """
    Cliente base para integrações com APIs empresariais
    Fornece funcionalidades comuns como autenticação, cache, rate limiting
    """

    def __init__(self, base_url: str, api_key: Optional[str] = None, timeout: int = 30):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key or self._get_api_key()
        self.timeout = timeout
        self.settings = get_settings()

        # Configuração HTTP
        self.client = httpx.AsyncClient(
            timeout=timeout,
            headers=self._get_default_headers()
        )

        # Cache simples em memória
        self.cache = {}
        self.cache_ttl = 300  # 5 minutos

        # Rate limiting
        self.requests_per_minute = 60
        self.request_times: List[datetime] = []

    @abstractmethod
    def _get_api_key(self) -> Optional[str]:
        """Retorna a chave da API das variáveis de ambiente"""
        pass

    def _get_default_headers(self) -> Dict[str, str]:
        """Headers padrão para todas as requisições"""
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'Analytics-Platform-Agent/1.0'
        }

        # Garantir que todos os valores sejam strings ASCII válidas
        for key, value in headers.items():
            if isinstance(value, str):
                try:
                    value.encode('ascii')
                except UnicodeEncodeError:
                    # Remover caracteres não-ASCII se houver
                    headers[key] = value.encode('ascii', 'ignore').decode('ascii')

        if self.api_key:
            # Cada API pode ter seu próprio método de autenticação
            # Será sobrescrito nas classes filhas
            pass

        return headers

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Faz uma requisição HTTP com tratamento de erros e cache
        """
        # Verificar rate limiting
        await self._check_rate_limit()

        # Preparar URL
        url = f"{self.base_url}{endpoint}"

        # Verificar cache
        cache_key = f"{method}:{url}:{json.dumps(params or {})}:{json.dumps(data or {})}"
        if use_cache and cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if datetime.now() - timestamp < timedelta(seconds=self.cache_ttl):
                return cached_data

        try:
            # Registrar timestamp da requisição
            self.request_times.append(datetime.now())

            # Fazer requisição
            response = await self.client.request(
                method=method.upper(),
                url=url,
                params=params,
                json=data
            )

            # Verificar status
            response.raise_for_status()

            # Processar resposta
            result = response.json() if response.content else {}

            # Salvar no cache
            if use_cache:
                self.cache[cache_key] = (result, datetime.now())

            return result

        except httpx.HTTPStatusError as e:
            return {
                "error": f"HTTP {e.response.status_code}: {e.response.text}",
                "status_code": e.response.status_code
            }
        except httpx.RequestError as e:
            return {
                "error": f"Erro de conexão: {str(e)}",
                "url": url
            }
        except Exception as e:
            return {
                "error": f"Erro inesperado: {str(e)}"
            }

    async def _check_rate_limit(self):
        """
        Verifica e controla o rate limiting
        """
        now = datetime.now()

        # Remover timestamps antigos (mais de 1 minuto)
        self.request_times = [
            t for t in self.request_times
            if now - t < timedelta(minutes=1)
        ]

        # Verificar se atingiu o limite
        if len(self.request_times) >= self.requests_per_minute:
            # Calcular tempo para esperar
            oldest_request = min(self.request_times)
            wait_time = 60 - (now - oldest_request).seconds

            if wait_time > 0:
                await asyncio.sleep(wait_time)

    async def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None, use_cache: bool = True) -> Dict[str, Any]:
        """Método GET"""
        return await self._make_request("GET", endpoint, params=params, use_cache=use_cache)

    async def post(self, endpoint: str, data: Optional[Dict[str, Any]] = None, use_cache: bool = False) -> Dict[str, Any]:
        """Método POST"""
        return await self._make_request("POST", endpoint, data=data, use_cache=use_cache)

    async def put(self, endpoint: str, data: Optional[Dict[str, Any]] = None, use_cache: bool = False) -> Dict[str, Any]:
        """Método PUT"""
        return await self._make_request("PUT", endpoint, data=data, use_cache=use_cache)

    async def delete(self, endpoint: str, use_cache: bool = False) -> Dict[str, Any]:
        """Método DELETE"""
        return await self._make_request("DELETE", endpoint, use_cache=use_cache)

    async def close(self):
        """Fecha o cliente HTTP"""
        await self.client.aclose()

    def clear_cache(self):
        """Limpa o cache"""
        self.cache.clear()
