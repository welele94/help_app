from __future__ import annotations

from .dominio import EntradaSessao
from .historico import Historico
from .pipeline import PipelineBase
from .mensagens import MensagemCatalogo



class HelpApp:
    def __init__(self, pipeline: PipelineBase, historico: Historico):
        self.pipeline = pipeline
        self.historico = historico

    def correr_sessao(self, msg: MensagemCatalogo, entrada: EntradaSessao) -> str:
        texto = self.pipeline.processar(msg, entrada)
        self.historico.registar(
            {
                "data": getattr(entrada, "data", ""),
                "estado": entrada.estado,
                "intensidade": entrada.intensidade,
                "mensagem": texto,
            }
        )
        return texto

    def ver_historico(self, n: int = 5) -> list[str]:
        return self.historico.obter_ultimas(n)
