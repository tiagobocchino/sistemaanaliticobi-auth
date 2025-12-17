"""
Sistema de Cache e Memória Contextual para Agentes IA
"""
import json
import hashlib
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from collections import OrderedDict
import os


class InMemoryCache:
    """Cache em memória com LRU (Least Recently Used) para fallback quando Redis não disponível"""

    def __init__(self, max_size: int = 1000, default_ttl: int = 3600):
        """
        Args:
            max_size: Tamanho máximo do cache
            default_ttl: TTL padrão em segundos (1 hora por padrão)
        """
        self.cache: OrderedDict = OrderedDict()
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.expiry: Dict[str, datetime] = {}

    def get(self, key: str) -> Optional[Any]:
        """Recupera valor do cache"""
        # Verificar expiração
        if key in self.expiry:
            if datetime.now() > self.expiry[key]:
                self._delete(key)
                return None

        # Mover para final (mais recente)
        if key in self.cache:
            self.cache.move_to_end(key)
            return self.cache[key]

        return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Armazena valor no cache"""
        # Remover item mais antigo se cache cheio
        if len(self.cache) >= self.max_size and key not in self.cache:
            oldest_key = next(iter(self.cache))
            self._delete(oldest_key)

        # Adicionar/atualizar item
        self.cache[key] = value
        self.cache.move_to_end(key)

        # Definir expiração
        ttl_seconds = ttl if ttl is not None else self.default_ttl
        self.expiry[key] = datetime.now() + timedelta(seconds=ttl_seconds)

    def delete(self, key: str) -> None:
        """Remove item do cache"""
        self._delete(key)

    def _delete(self, key: str) -> None:
        """Remoção interna"""
        if key in self.cache:
            del self.cache[key]
        if key in self.expiry:
            del self.expiry[key]

    def clear(self) -> None:
        """Limpa todo o cache"""
        self.cache.clear()
        self.expiry.clear()

    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do cache"""
        return {
            'size': len(self.cache),
            'max_size': self.max_size,
            'usage_percent': (len(self.cache) / self.max_size) * 100,
            'items': list(self.cache.keys())[:10]  # Primeiros 10 itens
        }


class RedisCache:
    """Cache distribuído usando Redis (opcional)"""

    def __init__(self):
        self.redis_client = None
        self.redis_enabled = False
        self._try_connect_redis()

    def _try_connect_redis(self):
        """Tenta conectar ao Redis"""
        try:
            import redis
            redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
            self.redis_client = redis.from_url(redis_url, decode_responses=True)
            # Testar conexão
            self.redis_client.ping()
            self.redis_enabled = True
            print(f"[OK] Redis cache conectado: {redis_url}")
        except ImportError:
            print("[INFO] Redis nao instalado. Use: pip install redis")
            self.redis_enabled = False
        except Exception as e:
            print(f"[INFO] Redis nao disponivel: {e}. Usando cache em memoria.")
            self.redis_enabled = False

    def get(self, key: str) -> Optional[Any]:
        """Recupera valor do Redis"""
        if not self.redis_enabled:
            return None

        try:
            value = self.redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            print(f"Erro ao ler do Redis: {e}")
            return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Armazena valor no Redis"""
        if not self.redis_enabled:
            return

        try:
            serialized = json.dumps(value, ensure_ascii=False)
            if ttl:
                self.redis_client.setex(key, ttl, serialized)
            else:
                self.redis_client.set(key, serialized)
        except Exception as e:
            print(f"Erro ao escrever no Redis: {e}")

    def delete(self, key: str) -> None:
        """Remove item do Redis"""
        if not self.redis_enabled:
            return

        try:
            self.redis_client.delete(key)
        except Exception as e:
            print(f"Erro ao deletar do Redis: {e}")

    def clear_pattern(self, pattern: str) -> None:
        """Remove todos os itens que correspondem ao padrão"""
        if not self.redis_enabled:
            return

        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                self.redis_client.delete(*keys)
        except Exception as e:
            print(f"Erro ao limpar padrão do Redis: {e}")


class CacheManager:
    """Gerenciador de cache híbrido (Redis + In-Memory)"""

    def __init__(self):
        self.redis_cache = RedisCache()
        self.memory_cache = InMemoryCache(max_size=500, default_ttl=1800)  # 30 min
        self.cache_prefix = "analytics_agent"

    def _make_key(self, namespace: str, key: str) -> str:
        """Gera chave de cache com namespace"""
        return f"{self.cache_prefix}:{namespace}:{key}"

    def _hash_key(self, data: Any) -> str:
        """Gera hash para usar como chave"""
        serialized = json.dumps(data, sort_keys=True, ensure_ascii=False)
        return hashlib.md5(serialized.encode()).hexdigest()

    def get(self, namespace: str, key: str) -> Optional[Any]:
        """
        Recupera valor do cache (tenta Redis primeiro, depois memória)

        Args:
            namespace: Namespace do cache ('api', 'query', 'analysis', etc)
            key: Chave do item

        Returns:
            Valor do cache ou None
        """
        cache_key = self._make_key(namespace, key)

        # Tentar Redis primeiro
        if self.redis_cache.redis_enabled:
            value = self.redis_cache.get(cache_key)
            if value is not None:
                return value

        # Fallback para memória
        return self.memory_cache.get(cache_key)

    def set(
        self,
        namespace: str,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> None:
        """
        Armazena valor no cache (Redis + memória)

        Args:
            namespace: Namespace do cache
            key: Chave do item
            value: Valor a armazenar
            ttl: Tempo de vida em segundos (None = padrão)
        """
        cache_key = self._make_key(namespace, key)

        # Armazenar em ambos
        if self.redis_cache.redis_enabled:
            self.redis_cache.set(cache_key, value, ttl)

        self.memory_cache.set(cache_key, value, ttl)

    def cache_api_call(
        self,
        api_name: str,
        endpoint: str,
        params: Optional[Dict] = None,
        ttl: int = 300  # 5 minutos por padrão
    ):
        """
        Decorator para cachear chamadas de API

        Args:
            api_name: Nome da API (sienge, cvdw, etc)
            endpoint: Endpoint chamado
            params: Parâmetros da chamada
            ttl: Tempo de cache em segundos

        Returns:
            Decorator function
        """
        def decorator(func):
            async def wrapper(*args, **kwargs):
                # Gerar chave de cache
                cache_data = {
                    'api': api_name,
                    'endpoint': endpoint,
                    'params': params or {},
                    'kwargs': {k: v for k, v in kwargs.items() if k != 'self'}
                }
                cache_key = self._hash_key(cache_data)

                # Tentar obter do cache
                cached = self.get('api_calls', cache_key)
                if cached is not None:
                    return cached

                # Executar função
                result = await func(*args, **kwargs)

                # Armazenar no cache
                self.set('api_calls', cache_key, result, ttl)

                return result

            return wrapper
        return decorator

    def invalidate_namespace(self, namespace: str) -> None:
        """Invalida todos os itens de um namespace"""
        pattern = f"{self.cache_prefix}:{namespace}:*"

        # Limpar Redis
        if self.redis_cache.redis_enabled:
            self.redis_cache.clear_pattern(pattern)

        # Limpar memória (padrão simples - limpa tudo)
        # Em produção, seria melhor iterar e deletar seletivamente
        if namespace in ['api_calls', 'queries']:
            self.memory_cache.clear()

    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do cache"""
        return {
            'redis_enabled': self.redis_cache.redis_enabled,
            'memory_cache': self.memory_cache.get_stats(),
            'namespaces': ['api_calls', 'queries', 'analysis', 'context']
        }


class ConversationMemory:
    """Gerencia memória contextual de conversas com usuários"""

    def __init__(self, cache_manager: CacheManager):
        self.cache = cache_manager
        self.max_history = 10  # Máximo de mensagens por usuário

    def save_message(
        self,
        user_id: str,
        message: str,
        response: str,
        metadata: Optional[Dict] = None
    ) -> None:
        """
        Salva mensagem na memória

        Args:
            user_id: ID do usuário
            message: Mensagem enviada
            response: Resposta gerada
            metadata: Metadados adicionais (data_sources, tools_used, etc)
        """
        history = self.get_history(user_id) or []

        # Adicionar nova mensagem
        history.append({
            'timestamp': datetime.now().isoformat(),
            'message': message,
            'response': response,
            'metadata': metadata or {}
        })

        # Manter apenas últimas N mensagens
        if len(history) > self.max_history:
            history = history[-self.max_history:]

        # Salvar (TTL de 24 horas)
        self.cache.set('conversation', user_id, history, ttl=86400)

    def get_history(self, user_id: str) -> Optional[List[Dict]]:
        """Recupera histórico de conversas do usuário"""
        return self.cache.get('conversation', user_id)

    def get_context(self, user_id: str, last_n: int = 3) -> str:
        """
        Gera contexto das últimas N conversas

        Args:
            user_id: ID do usuário
            last_n: Quantas conversas incluir

        Returns:
            String com contexto formatado
        """
        history = self.get_history(user_id)
        if not history:
            return "Sem histórico anterior."

        recent = history[-last_n:]
        context_lines = []

        for entry in recent:
            context_lines.append(f"Usuário: {entry['message']}")
            context_lines.append(f"Assistente: {entry['response'][:200]}...")  # Resumo

        return "\n".join(context_lines)

    def clear_user_history(self, user_id: str) -> None:
        """Limpa histórico de um usuário específico"""
        self.cache.memory_cache.delete(f"analytics_agent:conversation:{user_id}")
        self.cache.redis_cache.delete(f"analytics_agent:conversation:{user_id}")


# Instâncias globais
cache_manager = CacheManager()
conversation_memory = ConversationMemory(cache_manager)
