from enum import Enum
from prometheus_client import Gauge

from typing import Optional

_MAIN_LABEL_NAME = 'monitorName'


class TipoPrometheus(Enum):
    STATUS = 1              # [USO COMUM] status
    TEST_DURATION = 2       # [USO COMUM] duracao do teste
    STATUS_CODE = 3         # [HTTP] código http
    VERSION = 4             # [HTTP] versao do http
    SSL = 5                 # [HTTP] versao SSL usada


class Prometheus:
    _gauge_status: Gauge = Gauge(
        name='monitor_status',
        documentation='Status of the specific monitor',
        labelnames=[_MAIN_LABEL_NAME]
    )
    _gauge_test_duration: Gauge = Gauge(
        name='monitor_test_duration',
        documentation='Test duration for the specific monitor',
        labelnames=[_MAIN_LABEL_NAME]
    )
    _gauge_status_code: Gauge = Gauge(
        name='monitor_http_status_code',
        documentation='Status code of the last probe',
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
    def delete(cls, tipo: TipoPrometheus, label: str) -> None:
        """Semelhante ao `Delete` de um GaugeVec

        Args:
            tipo (TipoPrometheus): tipo de gauge a ser removido
            label (str): label do gauge a ser removido
        """
        x: Optional[Gauge] = cls._match(tipo)

        if x is None:
            raise RuntimeError(f'Tipo de gauge {tipo} não suportado')

        x.remove([label])
        return