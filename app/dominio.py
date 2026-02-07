from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from time import time_ns

@dataclass(frozen=True)
class EntradaSessao:
    estado: str
    intensidade: int
    utilizador: str
    # timestamp em nanos para evitar repetir mensagens em chamadas seguidas
    data: int = field(default_factory=time_ns)

class Mensagem(ABC):
    @abstractmethod
    def gerar_texto(self, entrada: EntradaSessao) -> str:
        ...
