from __future__ import annotations
from abc import ABC, abstractmethod


class IPersistencia(ABC):
    @abstractmethod
    def registar(self, entrada: dict) -> None:
        ...

    @abstractmethod
    def obter_ultimas(self, n: int) -> list[dict]:
        ...


class PersistenciaMemoria(IPersistencia):
    def __init__(self) -> None:
        self._dados: list[dict] = []

    def registar(self, entrada: dict) -> None:
        self._dados.append(entrada)

    def obter_ultimas(self, n: int) -> list[dict]:
        return self._dados[-n:]
