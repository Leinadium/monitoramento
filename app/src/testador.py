"""testador.py

Contém a implementação da classe Testador, que faz os testes do projeto
"""
import socket
import logging
from time import time
from requests import get, post, put, Response
from discord_webhook import DiscordWebhook
from requests.exceptions import ConnectTimeout, ConnectionError, JSONDecodeError

from armazenamento import Armazenamento
from enums import TipoMetodoHTTP, Status
from prom import TipoPrometheus, Prometheus
from models import Modulo, ConfigDiscord, ConfigStatuspage

from typing import Optional


class TestadorBase:
    """Classe base de um testador.

    Contém todos os métodos obrigatórios de um testador
    """

    VERSAO = '1.0'
    NOME = f'Monitor (Leinadium v{VERSAO})'

    def __init__(self,
                 modulo: Modulo,
                 armazenamento: Optional[Armazenamento] = None,
                 discord: Optional[ConfigDiscord] = None,
                 statuspage: Optional[ConfigStatuspage] = None
                 ):
        """Inicializa um testador

        Args:
            modulo (Modulo): Módulo a ser testado
            armazenamento (Armazenamento, optional): Armazenamento a ser usado. Default é None.
            discord (Discord, optional): Configurações do Discord. Default é None.
            statuspage (StatusPage, optional): Configurações do StatusPage. Default é None.
        """
        self.modulo: Modulo = modulo
        self.armazenamento: Optional[Armazenamento] = armazenamento

        # para o discord
        if discord is not None:
            self.discord: Optional[ConfigDiscord] = discord
            self.discord_url = f'https://discordapp.com/api/webhooks/{discord.ident}/{discord.token}'
        else:
            self.discord = None
            self.discord_url = None

        self.statuspage: Optional[ConfigStatuspage] = statuspage

        # variaveis para armazenar os resultados
        self.status: Optional[Status] = Status.UNKNOWN
        self.duracao: Optional[float] = None
        self.informacao_adicional: Optional[str] = None

    def testar_http(self):
        """Faz o teste para o módulo caso seja do tipo HTTP"""
        pass

    def testar_port(self):
        """Faz o teste para o módulo caso seja do tipo Port"""
        pass

    def testar_size(self):
        """Faz o teste para o módulo caso seja do tipo Size"""
        pass

    def testar_custom(self):
        """Faz o teste customizado do módulo"""
        pass

    def testar(self):
        """Testa o módulo

        Executa todos os casos de teste aplicáveis para o módulo.
        Caso o status do módulo seja diferente de nulo após todos os testes,
        então o resultado é armazenado no armazenamento.

        Além disso, são executadas as notificações para o discord e para a statuspage

        """
        _tempo = time()

        self.testar_http()
        self.testar_port()
        self.testar_size()
        self.testar_custom()

        self.duracao = time() - _tempo

        self.notificar_discord()
        self.notificar_statuspage()

        if self.status is not None:
            # atualiza o status do modulo
            Prometheus.get(TipoPrometheus.STATUS, self.modulo.nome).set(self.status.value)
            # atualiza a duracao do teste do modulo
            Prometheus.get(TipoPrometheus.TEST_DURATION, self.modulo.nome).set(self.duracao)

        if self.armazenamento:
            self.armazenamento.guardar(self.modulo.nome, self.status)

        logging.info("Teste realizado: {status: %s, duracao: %0.3fs, infos: %s}",
                     self.status.nome(),
                     self.duracao,
                     self.informacao_adicional
                     )

    def notificar_discord(self):
        """Notifica o status do módulo no Discord caso o status atual seja diferente do
        status armazenado no armazenamento.

        Caso o status seja OPERATIONAL, então a mensagem enviada no discord possuirá as seguintes propriedades:
            Content: <@&{infra_role}> + <@&{n}> para cada n em modulo.discord,
            Message Embed: {
                Title: "Alerta do Monitor: {nome do módulo}",
                Embed Author: "Monitor {versao do testador}",
                Color: "0x00FF00",
                Embed Footer: "Monitor {versao do testador}",
                Embed Fields: [
                    {Name: "Status", Value: "🟩 Operacional", Inline: False},
                    {Name: "Informações Adicionais", Value: informacoes_adicionais, Inline: False}
                ]
            }

        Caso o status seja outro, então a mensagem enviada no discord possuirá as seguintes propriedades:
            Content: <@&{infra_role}> + <@&{n}> para cada n em modulo.discord,
            Message Embed: {
                Title: "Alerta do Monitor: {nome do módulo}",
                Author: "Monitor {versao do testador}",
                Color: "0xFF0000",
                Embed Footer: "Monitor {versao do testador}",
                Embed Fields: [
                    {Name: "Status", Value: "⚠️Problemas", Inline: False},
                    {Name: "Informações Adicionais", Value: informacoes_adicionais, Inline: False}
                ]
            }
        """
        if self.discord is None or not self.armazenamento:
            # discord não configurado
            # ou armazenamento nao configurado
            # não há nada pra fazer aqui, pula
            return

        # pega o ultimo status do armazenamento
        ultimo_status: Status = self.armazenamento.coletar(self.modulo.nome)
        logging.debug(ultimo_status, self.status)
        if ultimo_status == self.status:
            # o status não mudou
            return

        # cria o conteudo da notificação (marcando os grupos especificos)
        content = f'<@&{self.discord.infra_role}>' + ''.join([
            f'<@&{n}>' for n in self.modulo.discords
        ])

        texto_status = "⚠️Problemas"
        cor = 0xff0000
        if self.status == Status.OPERATIONAL:
            texto_status = "🟩 Operacional"
            cor = 0x00ff00

        logging.info(
            "Enviando webhook do discord para o módulo %s com estado %s",
            self.modulo.nome,
            texto_status
        )

        # criando webhook
        webhook = DiscordWebhook(
            rate_limit_retry=True,
            url=self.discord_url,
            content=content,
            embeds=[{
                'title': f'Alerta do Monitor: {self.modulo.nome}',
                'author': {
                    'name': self.NOME
                },
                'color': cor,
                'footer': {
                    'text': self.NOME
                },
                'fields': [
                    {
                        'name': 'Status',
                        'value': texto_status,
                        'inline': False
                    },
                    {
                        'name': 'Informações Adicionais',
                        'value': self.informacao_adicional,
                        'inline': False
                    }
                ]
            }]
        )
        r: Response = webhook.execute()
        if not r.ok:
            logging.error("Erro ao enviar webhook discord para o módulo %s", self.modulo.nome)

    def notificar_statuspage(self):
        """Faz um request para a api da statuspage.io utilizando o component_id e o token do módulo.

        O request possui o identificador do component, o token, e o nome do status atual.
        Caso self.statuspage seja nulo, a função não executa nada.
        Caso self.status seja nulo, a função não executa nada
        """
        if self.statuspage is None or self.status is None:
            return

        r: Response = put(
            url=f'https://api.statuspage.io/v1/pages/{self.statuspage.page_id}/components/{self.modulo.statuspage}',
            headers={
                'Authorization': self.statuspage.api_key,
                'Content-Type': 'application/json',
            },
            data={
                'component': {
                    'status': self.status.nome()
                }
            }
        )

        if r.status_code in [401, 404, 422]:
            try:
                logging.error('Erro ao enviar componente para statuspage [%s]: %s', r.status_code, r.json()['message'])
            except KeyError:
                logging.error("Erro ao enviar component para statuspage, e a resposta json foi inválida")
        return


class TestadorHTTP(TestadorBase):
    def testar_http(self):
        _url = self.modulo.params.url
        _metodo = self.modulo.params.metodo
        self.status = Status.MAJOR_OUTAGE  # default status
        self.informacao_adicional = '-'

        try:
            if _metodo == TipoMetodoHTTP.GET:
                _resposta = get(_url, timeout=5)
            elif _metodo == TipoMetodoHTTP.POST:
                _resposta = post(_url, timeout=5)
            else:
                raise RuntimeError("Método HTTP não suportado")

            # atualiza o status do módulo
            if _resposta.status_code == 200:
                self.status = Status.OPERATIONAL
            elif _resposta.status_code > 500:
                self.status = Status.UNDER_MAINTENANCE
            else:
                self.status = Status.MAJOR_OUTAGE
            # atualiza a informacao adicional do módulo
            self.informacao_adicional = f'{_resposta.status_code} - {_resposta.reason}'
            Prometheus.get(TipoPrometheus.STATUS_CODE, self.modulo.nome).set(_resposta.status_code)

        except (ConnectTimeout, ConnectionError, RuntimeError) as e:
            logging.error("Erro ao testar HTTP do modulo %s: %s", self.modulo.nome, e)
            self.status = Status.MAJOR_OUTAGE
            self.informacao_adicional = str(e)
            # remove a informacao do modulo no prometheus
            Prometheus.delete(TipoPrometheus.STATUS_CODE, self.modulo.nome)


class TestadorPort(TestadorBase):
    def testar_port(self):
        self.status = Status.MAJOR_OUTAGE  # default status

        _socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        _socket.settimeout(1)

        # se conectar na porta, _status será True
        try:
            _port = self.modulo.params.port
            _url = self.modulo.params.url
            self.status = Status.OPERATIONAL if _socket.connect_ex((_url, _port)) == 0 else Status.MAJOR_OUTAGE
            _socket.close()
        except Exception as e:  # noqa
            logging.error("Erro ao testar PORT do modulo %s: %s", self.modulo.nome, e)
            self.status = Status.MAJOR_OUTAGE


class TestadorSize(TestadorBase):
    def testar_size(self):
        _url = self.modulo.params.url
        _metodo = self.modulo.params.metodo

        try:
            if _metodo == TipoMetodoHTTP.GET:
                _resposta = get(_url, timeout=5)
            elif _metodo == TipoMetodoHTTP.POST:
                _resposta = post(_url, timeout=5)
            else:
                raise RuntimeError("Método HTTP não suportado")

            status_code = _resposta.status_code
            conteudo = _resposta.json()
            porcentagem = conteudo['porcentagem']
            if porcentagem < 0.5:
                self.status = Status.OPERATIONAL
            elif porcentagem < 0.7:
                self.status = Status.DEGRADED_PERFORMANCE
            elif porcentagem < 0.9:
                self.status = Status.PARTIAL_OUTAGE
            else:
                self.status = Status.MAJOR_OUTAGE

            self.informacao_adicional = f'Ocupação: {porcentagem:.0%}'
            Prometheus.get(TipoPrometheus.SIZE, self.modulo.nome).set(porcentagem)
            Prometheus.get(TipoPrometheus.STATUS_CODE, self.modulo.nome).set(status_code)

        except (ConnectTimeout, ConnectionError, RuntimeError, JSONDecodeError, KeyError) as e:
            logging.error("Erro ao testar SIZE do modulo %s: %s", self.modulo.nome, e)
            self.status = None
            self.informacao_adicional = str(e)
            Prometheus.delete(TipoPrometheus.STATUS_CODE, self.modulo.nome)
            Prometheus.delete(TipoPrometheus.SIZE, self.modulo.nome)
