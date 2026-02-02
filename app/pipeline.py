from __future__ import annotations

from .dominio import Mensagem, EntradaSessao


class PipelineBase:
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def processar(self, msg: Mensagem, entrada: EntradaSessao) -> str:
        return msg.gerar_texto(entrada)


class NormalizeMixin:
    def processar(self, msg: Mensagem, entrada: EntradaSessao) -> str:
        texto = super().processar(msg, entrada)
        return " ".join(texto.strip().split())


class LoggingMixin:
    def __init__(self, logger=None, **kwargs):
        self.logger = logger
        super().__init__(**kwargs)

    def processar(self, msg: Mensagem, entrada: EntradaSessao) -> str:
        texto = super().processar(msg, entrada)
        if self.logger and hasattr(self.logger, "registar") and callable(self.logger.registar):
            self.logger.registar(f"[LOG] texto_final='{texto}'")
        return texto


class CacheUltimoMixin:
    def __init__(self, **kwargs):
        self.ultimo_texto = None
        super().__init__(**kwargs)

    def processar(self, msg: Mensagem, entrada: EntradaSessao) -> str:
        texto = super().processar(msg, entrada)
        self.ultimo_texto = texto
        return texto


class PipelineCompleto(LoggingMixin, CacheUltimoMixin, NormalizeMixin, PipelineBase):
    pass


class PipelineSemCache(LoggingMixin, NormalizeMixin, PipelineBase):
    pass
