from enum import Enum
from prometheus_client import Gauge

from typing import Optional

_MAIN_LABEL_NAME = 'monitorName'


class TipoPrometheus(Enum):
    STATUS = 1              # [USO COMUM] status
    TEST_DURATION = 2       # [USO COMUM] duracao do teste
    STATUS_CODE = 3         # [HTTP] código http
    # VERSION = 4             # [HTTP] versao do http
    # SSL = 5                 # [HTTP] versao SSL usada
    SIZE = 6                # [SIZE] espaço (bytes) livres


class Prometheus:
    """Classe contendo os gauges para serem coletados pelo processo do Prometheus

    Os Gauges implementados são:
        status,
        test_duration,
        status_code
    """
    _gauge_status: Optional[Gauge] = None
    _gauge_test_duration: Optional[Gauge] = None
    _gauge_status_code: Optional[Gauge] = None
    _gauge_size: Optional[Gauge] = None

    @classmethod
    def start(cls):
        """Cria os Gauges do Prometheus

        Necessário ser executado antes de usar as outras funções
        """
        cls._gauge_status = Gauge(
            name='monitor_status',
            documentation='Status of the specific monitor',
            labelnames=[_MAIN_LABEL_NAME]
        )
        cls._gauge_test_duration: Gauge = Gauge(
            name='monitor_test_duration',
            documentation='Test duration for the specific monitor',
            labelnames=[_MAIN_LABEL_NAME]
        )
        cls._gauge_status_code: Gauge = Gauge(
            name='monitor_http_status_code',
            documentation='Status code of the last probe',
            labelnames=[_MAIN_LABEL_NAME]
        )
        cls._gauge_size: Gauge = Gauge(
            name='monitor_size',
            documentation='Free space available for the specific monitor',
            labelnames=[_MAIN_LABEL_NAME]
        )

    @classmethod
    def _match(cls, tipo: TipoPrometheus) -> Optional[Gauge]:
        """Retorna a variavel correta de acordo com o tipo"""
        if tipo == TipoPrometheus.STATUS:
            return cls._gauge_status
        elif tipo == TipoPrometheus.TEST_DURATION:
            return cls._gauge_test_duration
        elif tipo == TipoPrometheus.STATUS_CODE:
            return cls._gauge_status_code
        elif tipo == TipoPrometheus.SIZE:
            return cls._gauge_size
        else:
            return None

    @classmethod
    def get(cls, tipo: TipoPrometheus, label: str) -> Gauge:
        """Semelhante ao `With` de um GaugeVec

        Args:
            tipo (TipoPrometheus): tipo de gauge solicitado
            label (str): label do gauge a ser selecionado
        """
        x: Optional[Gauge] = cls._match(tipo)

        if x is None:
            raise RuntimeError(f'Tipo de gauge {tipo} não suportado')

        return x.labels([label])

    @classmethod
    def delete(cls, tipo: TipoPrometheus, _label: str) -> None:
        """Semelhante ao `Delete` de um GaugeVec

        OBS: Não está sendo possível remover labels. Por isso,
        essa função simplesmente não faz nada

        Args:
            tipo (TipoPrometheus): tipo de gauge a ser removido
            _label (str): label do gauge a ser removido
        """
        x: Optional[Gauge] = cls._match(tipo)

        if x is None:
            raise RuntimeError(f'Tipo de gauge {tipo} não suportado')

        # x.remove(label)               # -> KeyError
        # x.labels([label]).clear()     # -> no ._lock in Gauge
        return
