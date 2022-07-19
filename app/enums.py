from enum import Enum


class TipoModulo(Enum):
    """Tipos possíveis de módulo"""
    HTTP = 1
    PORT = 2


class TipoMetodoHTTP(Enum):
    """Tipos possíveis de método HTTP"""
    GET = 1
    POST = 2


class Status(Enum):
    """Status de um teste"""
    UNKNOWN = 0
    OPERATIONAL = 1
    MAJOR_OUTAGE = 2
    PARTIAL_OUTAGE = 3
    DEGRADED_PERFORMANCE = 4
    UNDER_MAINTENANCE = 5

    def nome(self) -> str:
        if self.name == 'UNKNOWN':
            return ''
        elif self.name == 'OPERATIONAL':
            return 'operational'
        elif self.name == 'MAJOR_OUTAGE':
            return 'major_outage'
        elif self.name == 'PARTIAL_OUTAGE':
            return 'partial_outage'
        elif self.name == 'DEGRADED_PERFORMANCE':
            return 'degraded_performance'
        elif self.name == 'UNDER_MAINTENANCE':
            return 'under_maintenance'
        else:
            return ''
