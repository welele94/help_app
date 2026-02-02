from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass(frozen=True)
class EntradaSessao:
    estado: str
    intensidade: int
    utilizador: str

class Mensagem(ABC):
    @abstractmethod
    def gerar_texto(self, entrada: EntradaSessao) -> str:
        ...
