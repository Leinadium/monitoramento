"""armazenamento.py

Contém a implementação do armazenamento de informações para o projeto.

Utiliza o banco de dados Redis
"""
# global packages
from redis import Redis
# local packages
from .enums import Status
# typing packages
from typing import Optional


class Armazenamento:
    def __init__(self, host: str, port: int, identificador: str = 'monitor'):
        """Inicia uma conexão com o armazenamento

        Args:
            host (str): host de conexão com o redis
            port (str): porta de conexão com o redis
            identificador (str): identificador a ser usado no redis
        """
        self._client: Redis = Redis(host=host, port=port)
        self._identificador = identificador

    def _get_redis_key(self, chave: str) -> str:
        """Retorna a chave a ser usada no Redis

        Args:
            chave (str): chave usada para gerar a chave real a ser usada no redis
        """
        return f'{self._identificador}:{chave}'

    def coletar(self, chave) -> Optional[Status]:
        """Coleta um status do banco de dados

        Args:
            chave (str): chave para ser coletada do banco de dados
        """
        x: Optional[bytes] = self._client.get(self._get_redis_key(chave))
        ret: Optional[Status] = None
        if x.isdigit():
            try:
                ret = Status(int(x))
            except ValueError:
                pass
        return ret

    def guardar(self, chave: str, valor: Status):
        """Armazena um status no banco de dados

        Args:
            chave (str): chave a ser usada para armazenar o valor
            valor (str): valor a ser armazenado no banco de dados
        """
        if isinstance(valor, Status):
            v = valor.value
        elif isinstance(valor, int):
            v = valor
        else:
            raise RuntimeError(f"Valor inválido para ser armazenado: {valor}")
        self._client.set(self._get_redis_key(chave), v)
