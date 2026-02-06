from __future__ import annotations

import json
import unicodedata
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
    Ex: data/perfis/micael.json
    """

    def __init__(self, base_dir: str | Path):
        self._base = Path(base_dir)
        self._base.mkdir(parents=True, exist_ok=True)

    def _normalizar_nome(self, nome: str) -> str:
        nome = nome.strip().lower()
        nome = unicodedata.normalize("NFD", nome)
        nome = "".join(c for c in nome if unicodedata.category(c) != "Mn")
        return nome

    def _slug(self, nome_norm: str) -> str:
        # nome_norm já vem normalizado (sem acentos, lower)
        seguro = "".join(ch for ch in nome_norm if ch.isalnum() or ch in ("_", "-"))
        return seguro or "utilizador"

    def _path(self, nome: str) -> Path:
        nome_norm = self._normalizar_nome(nome)
        return self._base / f"{self._slug(nome_norm)}.json"

    def existe(self, nome: str) -> bool:
        return self._path(nome).exists()

    def carregar(self, nome: str) -> PerfilUtilizador:
        nome_norm = self._normalizar_nome(nome)
        path = self._base / f"{self._slug(nome_norm)}.json"

        if not path.exists():
            perfil = PerfilUtilizador(nome=nome_norm)
            self.guardar(perfil)
            return perfil

        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)

        # Garantia mínima: se no ficheiro não vier nome, força o nome_norm
        if "nome" not in data or not data["nome"]:
            data["nome"] = nome_norm

        # Se o PerfilUtilizador tiver campos novos no código que não existam no JSON,
        # isto ainda funciona se esses campos tiverem default no dataclass.
        return PerfilUtilizador(**data)
    
    
    def guardar(self, perfil: PerfilUtilizador) -> None:
        # garante consistência: grava SEMPRE no path normalizado
        path = self._path(perfil.nome)
        with path.open("w", encoding="utf-8") as f:
            json.dump(asdict(perfil), f, ensure_ascii=False, indent=2)
