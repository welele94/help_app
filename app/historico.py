from __future__ import annotations

from .persistence import IPersistencia


class Historico:
    def __init__(self, persistencia: IPersistencia) -> None:
        self._p = persistencia

    def registar(self, texto: str) -> None:
        self._p.registar(texto)

    def obter_ultimas(self, n: int) -> list[str]:
        return self._p.obter_ultimas(n)
