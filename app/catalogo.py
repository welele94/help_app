from __future__ import annotations
import json
import hashlib
import unicodedata
from pathlib import Path
from typing import Dict, List

from .dominio import EntradaSessao


class CatalogoMensagens:
    def __init__(self, json_path: str | Path):
        self._path = Path(json_path)
        with self._path.open("r", encoding="utf-8") as f:
            self._data: Dict[str, List[str]] = json.load(f)

    def estados(self) -> list[str]:
        return sorted(self._data.keys())
    
    def normalizar_estado(self, estado:str) -> str:
        estado = estado.strip().lower()
        estado = unicodedata.normalize("NFD", estado)
        estado = "".join(c for c in estado if unicodedata.category(c) != "Mn")

        mapa = {
            "ansiosa": "ansioso",
            "zangada": "zangado",
            "motivada": "motivado",
            "calma": "calmo",
            "cansada": "cansado"
        }

        return mapa.get(estado, estado)

    def validar_minimo(self, estados: list[str], minimo: int = 50) -> None:
        for estado in estados:
            msgs = self._data.get(estado, {})
            total = 0

            if isinstance(msgs, dict):
                for _, lst in msgs.items():
                    total += len(lst)
            else:
                total = len(msgs)

            if total < minimo:
                raise ValueError(f"Estado '{estado}' tem {total} mensagens (minimo {minimo}).")

    def obter(self, estado: str, entrada: EntradaSessao) -> str:
        msgs = self._data.get(estado, [])
        if isinstance(msgs, dict):
            msgs = msgs.get(str(max(1, min(5, entrada.intensidade))), [])
        if not msgs:
            return "Estou aqui contigo. Vamos com calma."

        # determinístico (sem random)
        data = getattr(entrada, "data", "")
        chave = f"{estado}|{entrada.intensidade}|{getattr(entrada, 'utilizador', '')}|{data}"
        h = hashlib.sha256(chave.encode("utf-8")).hexdigest()
        idx = int(h[:8], 16) % len(msgs)
        return str(msgs[idx]).strip()