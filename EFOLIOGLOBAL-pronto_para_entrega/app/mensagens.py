from __future__ import annotations

from .dominio import Mensagem, EntradaSessao
from .catalogo import CatalogoMensagens


class MensagemCatalogo(Mensagem):
    def __init__(self, catalogo: CatalogoMensagens):
        self._catalogo = catalogo

    def gerar_texto(self, entrada: EntradaSessao) -> str:
        return self._catalogo.obter(entrada.estado, entrada)
