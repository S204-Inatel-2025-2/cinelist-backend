# app/core/cache.py
import redis
import os
import json

# O Railway injeta esta variável de ambiente automaticamente
REDIS_URL = os.getenv("REDIS_URL")
redis_client = None

if REDIS_URL:
    try:
        # decode_responses=True faz o redis retornar strings em vez de bytes
        pool = redis.ConnectionPool.from_url(REDIS_URL, decode_responses=True)
        redis_client = redis.Redis(connection_pool=pool)
        redis_client.ping()
        print("Conectado ao cache Redis com sucesso!")
    except Exception as e:
        print(f"Aviso: Falha ao conectar ao Redis. O cache está desabilitado. Erro: {e}")
        redis_client = None
else:
    print("Aviso: REDIS_URL não definida. O cache está desabilitado.")

def get_from_cache(key: str):
    """
    Busca um valor do cache Redis. Retorna None se não encontrar ou se o Redis estiver offline.
    """
    if not redis_client:
        return None
    try:
        data = redis_client.get(key)
        return json.loads(data) if data else None
    except Exception as e:
        print(f"Erro ao LER do cache Redis (key: {key}): {e}")
        return None

def set_to_cache(key: str, value: any, ttl_seconds: int):
    """
    Salva um valor no cache Redis com um tempo de expiração (TTL).
    """
    if not redis_client:
        return
    try:
        # Serializa o objeto Python (lista/dicionário) para uma string JSON
        data = json.dumps(value)
        # setex = SET com EXpiração (TTL)
        redis_client.setex(key, ttl_seconds, data)
    except Exception as e:
        print(f"Erro ao ESCREVER no cache Redis (key: {key}): {e}")