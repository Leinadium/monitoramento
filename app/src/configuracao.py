"""configuracao.py

Contém a classe Configuracao, que permite criar todos os modelos de configuração a partir de um arquivo TOML

Um exemplo de arquivo TOML pode ser encontrado em `example.config.toml`
"""

import tomli
import logging

from enums import TipoModulo, TipoMetodoHTTP
from models import ParamsHTTP, ParamsPort, ParamsSize
from models import Modulo, ConfigDiscord, ConfigStatuspage, ConfigRedis

from typing import Dict, List, Optional


class InvalidConfigFile(BaseException):
    """Representa uma exceção ao ler um arquivo TOML inválido"""
    pass


class Configuracao:
    """Classe que implementa a leitura do arquivo de configuração"""
    def __init__(self, path_para_arquivo: str):
        """Uma instancia contendo as configurações do arquivo fornecido

        Args:
            path_para_arquivo (str): path para o arquivo TOML

        Raises:
            FileNotFoundError: caso o arquivo não seja encontrado
            InvalidConfigFile: caso o arquivo de configuração não exista
        """

        # le o arquivo de configuração
        try:
            with open(path_para_arquivo, 'rb') as f:
                self._json: Dict = tomli.load(f)
        except FileNotFoundError:
            logging.error("Arquivo %s não encontrado", path_para_arquivo)
            exit(-1)

        # prepara as variaveis
        self._interval: int = -1
        self._porta: int = -2
        self._statuspage: Optional[ConfigStatuspage] = None
        self._discord: Optional[ConfigDiscord] = None
        self._redis: Optional[ConfigRedis] = None
        self._modules: List[Modulo] = []

        # faz o parsing do json
        try:
            self._interval = self._json['interval']
            self._porta = self._json['port']
            self._statuspage = ConfigStatuspage(
                page_id=self._json['statuspage']['apikey'],
                api_key=self._json['statuspage']['pageid']
            )
            self._discord = ConfigDiscord(
                infra_role=self._json['discord']['role_id'],
                ident=self._json['discord']['id'],
                token=self._json['discord']['token']
            )
            self._redis = ConfigRedis(
                host=self._json['redis']['host'],
                port=self._json['redis']['port']
            )
            # indo para cada modulo encontrado
            for m in self._json['modules']:
                nome = m['name']
                statuspage_id = m['statuspage_id']
                notify = m.get('notify')

                # acessando cada teste dentro do modulo
                for t in m['test']:
                    if t['type'] == 'http':
                        tipo = TipoModulo.HTTP
                        params = ParamsHTTP(
                            url=t['url'],
                            metodo=TipoMetodoHTTP.GET if t['method'].lower() == 'get' else TipoMetodoHTTP.POST
                        )
                    elif t['type'] == 'port':
                        tipo = TipoModulo.PORT
                        params = ParamsPort(
                            host=t['host'],
                            port=t['port']
                        )
                    elif t['type'] == 'size':
                        tipo = TipoModulo.SIZE
                        params = ParamsSize(
                            url=t['url'],
                            metodo=TipoMetodoHTTP.GET if t['method'].lower() == 'get' else TipoMetodoHTTP.POST

                        )
                    else:
                        # tipo invalido. pulando...
                        continue

                    # adicionando um modulo para cada teste
                    self._modules.append(
                        Modulo(nome, tipo, params, notify, statuspage_id)
                    )

        except KeyError as e:
            logging.exception("Chave não encontrada na configuração: %s", e)
            raise InvalidConfigFile()
        except ValueError as e:
            logging.exception("Valor inválido na configuração: %s", e)
            raise InvalidConfigFile()
        except IndexError as e:
            logging.exception("Indice inválido na configuração: %s", e)
            raise InvalidConfigFile()

    @property
    def interval(self) -> int:
        """Intervalo entre os testes"""
        if self._interval is None:
            raise RuntimeError("Configuração não efetuada com sucesso [interval é None]")
        return self._interval

    @property
    def port(self):
        """Porta para servir o client para o prometheus"""
        if self._porta is None:
            raise RuntimeError("Configuração não efetuada com sucesso [porta é None]")
        return self._porta

    @property
    def statuspage(self) -> ConfigStatuspage:
        """Configurações da statuspage"""
        return self._statuspage

    @property
    def discord(self) -> ConfigDiscord:
        """Configurações do discord"""
        return self._discord

    @property
    def redis(self) -> ConfigRedis:
        """Configurações do redis"""
        return self._redis

    @property
    def modules(self) -> List[Modulo]:
        """Lista de módulos a serem testados"""
        if not self._modules:
            raise RuntimeError("Lista de módulos vazia")
        return self._modules




