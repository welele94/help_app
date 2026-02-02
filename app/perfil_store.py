from __future__ import annotations

import json
from abc import ABC, abstractmethod
from dataclasses import asdict
from pathlib import Path

from .perfil import PerfilUtilizador


class IPerfilStore(ABC):
    @abstractmethod
    def carregar(self, nome: str) -> PerfilUtilizador:
        raise NotImplementedError

    @abstractmethod
    def guardar(self, perfil: PerfilUtilizador) -> None:
        raise NotImplementedError


class PerfilStoreJSON(IPerfilStore):
    """
    Guarda um perfil por utilizador em JSON.
    Ex: help_app/data/perfis/micael.json
    """

    def __init__(self, base_dir: str | Path):
        self._base = Path(base_dir)
        self._base.mkdir(parents=True, exist_ok=True)

    def _path(self, nome: str) -> Path:
        seguro = "".join(ch for ch in nome.strip().lower() if ch.isalnum() or ch in ("_", "-"))
        if not seguro:
            seguro = "utilizador"
        return self._base / f"{seguro}.json"

    def carregar(self, nome: str) -> PerfilUtilizador:
        p = self._path(nome)
        if not p.exists():
            return PerfilUtilizador(nome=nome.strip() or "Utilizador")

        with p.open("r", encoding="utf-8") as f:
            data = json.load(f)

        # tolerante a evoluções (campos extra/ausentes)
        perfil = PerfilUtilizador(nome=data.get("nome", nome))
        perfil.total_sessoes = int(data.get("total_sessoes", 0))
        perfil.contagem_estados = dict(data.get("contagem_estados", {}))
        perfil.soma_intensidade = dict(data.get("soma_intensidade", {}))
        return perfil

    def guardar(self, perfil: PerfilUtilizador) -> None:
        p = self._path(perfil.nome)
        with p.open("w", encoding="utf-8") as f:
            json.dump(asdict(perfil), f, ensure_ascii=False, indent=2)
