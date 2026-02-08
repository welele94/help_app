from __future__ import annotations

from .persistence import IPersistencia


class Historico:
    def __init__(self, persistencia: IPersistencia) -> None:
        self._p = persistencia

    def registar(self, entrada: dict) -> None:
        self._p.registar(entrada)

    def obter_ultimas(self, n: int) -> list[dict]:
        return self._p.obter_ultimas(n)
