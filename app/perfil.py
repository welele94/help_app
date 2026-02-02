from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict


@dataclass
class PerfilUtilizador:
    nome: str
    total_sessoes: int = 0
    contagem_estados: Dict[str, int] = field(default_factory=dict)
    soma_intensidade: Dict[str, int] = field(default_factory=dict)

    def registar_sessao(self, estado: str, intensidade: int) -> None:
        self.total_sessoes += 1
        self.contagem_estados[estado] = self.contagem_estados.get(estado, 0) + 1
        self.soma_intensidade[estado] = self.soma_intensidade.get(estado, 0) + int(intensidade)

    def media_intensidade(self, estado: str) -> float:
        c = self.contagem_estados.get(estado, 0)
        if c == 0:
            return 0.0
        return self.soma_intensidade.get(estado, 0) / c
