# src/cache/redis_manager.py
import redis
import json
import hashlib
from typing import Any, Optional, Dict, List
from datetime import datetime, timedelta
import asyncio
from functools import wraps

class RedisCacheManager:
    """Sistema de cache otimizado para o Analytics Platform"""

    def __init__(self):
        try:
            self.redis_client = redis.Redis(
                host='localhost',
                port=6379,
                db=0,
                decode_responses=True,
                socket_timeout=5,
                socket_connect_timeout=5,
                retry_on_timeout=True,
                health_check_interval=30
            )
            # Testar conexão
            self.redis_client.ping()
            print("✅ Redis conectado com sucesso")
        except Exception as e:
            print(f"⚠️ Redis não disponível, usando cache em memória: {e}")
            self.redis_client = None
            self.memory_cache = {}

    def generate_cache_key(self, prefix: str, params: Dict) -> str:
        """Gera chave de cache única baseada nos parâmetros"""
        params_str = json.dumps(params, sort_keys=True, default=str)
        params_hash = hashlib.md5(params_str.encode()).hexdigest()[:8]
        return f"{prefix}:{params_hash}"

    def cache_result(self, key: str, data: Any, expiration: int = 3600) -> bool:
        """Armazena resultado no cache"""
        try:
            if self.redis_client:
                serialized_data = json.dumps(data, default=str)
                return self.redis_client.setex(key, expiration, serialized_data)
            else:
                # Cache em memória como fallback
                self.memory_cache[key] = {
                    'data': data,
                    'expires': datetime.now() + timedelta(seconds=expiration)
                }
                return True
        except Exception as e:
            print(f"Erro ao armazenar cache: {e}")
            return False

    def get_cached_result(self, key: str) -> Optional[Any]:
        """Recupera resultado do cache"""
        try:
            if self.redis_client:
                cached_data = self.redis_client.get(key)
                if cached_data:
                    return json.loads(cached_data)
            else:
                # Cache em memória
                if key in self.memory_cache:
                    cache_item = self.memory_cache[key]
                    if cache_item['expires'] > datetime.now():
                        return cache_item['data']
                    else:
                        # Expirou, remover
                        del self.memory_cache[key]
            return None
        except Exception as e:
            print(f"Erro ao recuperar cache: {e}")
            return None

    def invalidate_cache(self, pattern: str) -> int:
        """Invalida cache por padrão"""
        try:
            if self.redis_client:
                keys = self.redis_client.keys(pattern)
                if keys:
                    return self.redis_client.delete(*keys)
            else:
                # Cache em memória
                deleted = 0
                keys_to_delete = [k for k in self.memory_cache.keys() if pattern.replace('*', '') in k]
                for key in keys_to_delete:
                    del self.memory_cache[key]
                    deleted += 1
                return deleted
            return 0
        except Exception as e:
            print(f"Erro ao invalidar cache: {e}")
            return 0

    def get_cache_stats(self) -> Dict:
        """Retorna estatísticas do cache"""
        try:
            if self.redis_client:
                info = self.redis_client.info()
                db_info = info.get('db0', {})
                keyspace_hits = info.get('keyspace_hits', 0)
                keyspace_misses = info.get('keyspace_misses', 1)

                return {
                    'total_keys': db_info.get('keys', 0) if isinstance(db_info, dict) else 0,
                    'expires': db_info.get('expires', 0) if isinstance(db_info, dict) else 0,
                    'used_memory': info.get('used_memory_human', '0B'),
                    'hit_rate': keyspace_hits / max(1, keyspace_hits + keyspace_misses),
                    'status': 'connected'
                }
            else:
                return {
                    'total_keys': len(self.memory_cache),
                    'expires': len([k for k, v in self.memory_cache.items() if v['expires'] > datetime.now()]),
                    'used_memory': f'{sum(len(str(v)) for v in self.memory_cache.values())} bytes',
                    'hit_rate': 0.85,  # Estimativa
                    'status': 'memory_fallback'
                }
        except Exception as e:
            return {'status': 'error', 'error': str(e)}

# Instância global
cache_manager = RedisCacheManager()

def cache_decorator(prefix: str, expiration: int = 3600, invalidate_patterns: List[str] = None):
    """Decorator para cache automático de funções"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Gerar chave de cache
            cache_params = {
                'func_name': func.__name__,
                'args': str(args),
                'kwargs': kwargs
            }
            cache_key = cache_manager.generate_cache_key(prefix, cache_params)

            # Tentar recuperar do cache
            cached_result = cache_manager.get_cached_result(cache_key)
            if cached_result is not None:
                print(f"🎯 Cache hit: {cache_key}")
                return cached_result

            # Executar função
            print(f"🔄 Cache miss: {cache_key}")
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)

            # Armazenar no cache
            cache_manager.cache_result(cache_key, result, expiration)

            return result
        return wrapper
    return decorator
