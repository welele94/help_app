from __future__ import annotations
from abc import ABC, abstractmethod


class IPersistencia(ABC):
    @abstractmethod
    def registar(self, texto: str) -> None:
        ...

    @abstractmethod
    def obter_ultimas(self, n: int) -> list[str]:
        ...


class PersistenciaMemoria(IPersistencia):
    def __init__(self) -> None:
        self._dados: list[str] = []

    def registar(self, texto: str) -> None:
        self._dados.append(texto)

    def obter_ultimas(self, n: int) -> list[str]:
        return self._dados[-n:]
