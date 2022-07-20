"""modulo.py

Contém a implementação da dataclass `Modulo`,
que permite armazenar informações sobre um módulo a ser testado
"""

__all__ = ["ParamsHTTP", "ParamsPort", "Modulo", "ConfigDiscord", "ConfigStatuspage", "ConfigRedis"]

from dataclasses import dataclass

from .enums import TipoModulo, TipoMetodoHTTP

from typing import List, Union


@dataclass
class ParamsHTTP:
    """Parâmetros de um módulo HTTP"""
    url: str
    metodo: TipoMetodoHTTP


@dataclass
class ParamsPort:
    """Parâmetros de um módulo PORT"""
    host: str
    port: int


@dataclass
class Modulo:
    """Informações de um módulo a ser testado"""
    nome: str
    tipo: TipoModulo
    params: Union[ParamsHTTP, ParamsPort]
    discords: List[str]
    statuspage: str


@dataclass
class ConfigDiscord:
    """Informações relativas à configuração do Discord"""
    infra_role: str
    ident: str
    token: str


@dataclass
class ConfigStatuspage:
    """Informações relativas à configuração do StatusPage"""
    api_key: str
    page_id: str


@dataclass
class ConfigRedis:
    """Informações relativas à configuração da conexão com o Redis"""
    host: str
    port: int
