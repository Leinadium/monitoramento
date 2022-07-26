"""main.py

Contém o script para iniciar o loop de testadores
e do client do prometheus
"""
import logging
from time import sleep
from threading import Thread
from prometheus_client import start_http_server

from prom import Prometheus
from enums import TipoModulo
from configuracao import Configuracao
from armazenamento import Armazenamento
from testador import TestadorPort, TestadorHTTP, TestadorSize

from typing import List
from models import Modulo
from testador import TestadorBase

if __name__ == "__main__":
    # biblioteca de log
    logging.basicConfig(
        format='%(asctime)s [%(threadName)s] [%(levelname)s]: %(message)s',
        datefmt='%Y-%m-%d %H-%M-%S',
        level=logging.INFO
    )

    # cria as configurações
    c = Configuracao('config2.toml')
    logging.info("Configurações carregadas")

    # cria os gauges do client do prometheus
    Prometheus.start()
    start_http_server(port=c.port)
    logging.info(f"Servindo client na porta {c.port}")

    # criando os testadores
    testadores: List[TestadorBase] = []
    for m in c.modules:     # type: Modulo
        if m.tipo == TipoModulo.HTTP:
            testador = TestadorHTTP(
                modulo=m,
                armazenamento=Armazenamento(c.redis.host, c.redis.port),
                discord=c.discord,
                statuspage=c.statuspage
            )
        elif m.tipo == TipoModulo.PORT:
            testador = TestadorPort(
                modulo=m,
                armazenamento=Armazenamento(c.redis.host, c.redis.port),
                discord=c.discord,
                statuspage=c.statuspage
            )
        elif m.tipo == TipoModulo.SIZE:
            testador = TestadorSize(
                modulo=m,
                armazenamento=Armazenamento(c.redis.host, c.redis.port),
                discord=c.discord,
                statuspage=c.statuspage
            )
        else:
            raise NotImplemented(f"Tipo de módulo {m.tipo.name} não suportado")

        testadores.append(testador)
    logging.info("%d testadores carregados e criados", len(testadores))

    # loop dos testadores
    logging.info("Iniciando loop dos testadores")
    while True:
        for t in testadores:
            # cria uma thread para cada testador e executa
            logging.info("Executando testador [%s]", t.modulo.nome)
            thread = Thread(target=t.testar, name=f'thread-{t.modulo.nome}')
            thread.start()

        try:
            sleep(c.interval)
        except KeyboardInterrupt:
            # para o loop com um CTRL+C
            break

    logging.info("Fechando...")
