from __future__ import annotations
import json
import hashlib
from pathlib import Path
from typing import Dict, List

from .dominio import EntradaSessao


class CatalogoMensagens:
    def __init__(self, json_path: str | Path):
        self._path = Path(json_path)
        with self._path.open("r", encoding="utf-8") as f:
            self._data: Dict[str, List[str]] = json.load(f)

    def validar_minimo(self, estados: list[str], minimo: int = 50) -> None:
        for estado in estados:
            msgs = self._data.get(estado, [])
            if len(msgs) < minimo:
                raise ValueError(f"Estado '{estado}' tem {len(msgs)} mensagens (mínimo {minimo}).")

    def obter(self, estado: str, entrada: EntradaSessao) -> str:
        msgs = self._data.get(estado, [])
        if not msgs:
            return "Estou aqui contigo. Vamos com calma."

        # determinístico (sem random)
        chave = f"{entrada.estado}|{entrada.intensidade}|{getattr(entrada, 'utilizador', '')}"
        h = hashlib.sha256(chave.encode("utf-8")).hexdigest()
        idx = int(h[:8], 16) % len(msgs)
        return str(msgs[idx]).strip()
