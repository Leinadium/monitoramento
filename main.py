# global packages
from time import sleep
from threading import Thread
from prometheus_client import start_http_server
# local packages
from app.models import TipoModulo
from app.armazenamento import Armazenamento
from app.configuracao import Configuracao
from app.testador import TestadorPort, TestadorHTTP
# typing packages
from typing import List
from app.models import Modulo
from app.testador import TestadorBase

if __name__ == "__main__":
    # cria as configurações
    c = Configuracao('config.toml')

    # importa o prom para ele inicializar os gauges
    import app.prom

    # inicializa o prometheus
    start_http_server(port=c.port)
    print(f"Servindo status na porta {c.port}")

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
        else:
            raise NotImplemented(f"Tipo de módulo {m.tipo.name} não suportado")

        testadores.append(testador)

    # loop dos testadores
    while True:
        for t in testadores:
            # cria uma thread para cada testador e executa
            print(f"Executando testador {t.modulo.nome}")
            thread = Thread(target=t.testar)
            thread.start()
        # no final de tudo, dorme o tempo necessario
        print(f"Indo dormir por {c.interval} segundos")
        try:
            sleep(c.interval)
        except KeyboardInterrupt:
            break

    print("Fechando...")

