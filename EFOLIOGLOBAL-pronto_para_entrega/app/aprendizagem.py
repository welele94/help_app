from __future__ import annotations

from .perfil import PerfilUtilizador
from .dominio import EntradaSessao


class AprendizagemBasica:
    """
    Política de aprendizagem simples:
    - conta estados
    - acumula intensidade por estado
    """

    def atualizar(self, perfil: PerfilUtilizador, entrada: EntradaSessao) -> None:
        perfil.registar_sessao(entrada.estado, entrada.intensidade)
