from __future__ import annotations

from pathlib import Path
import sys
from datetime import date

from ui.rich_ui import (
    cabecalho,
    pedir_estado,
    mostrar_resposta,
    mostrar_historico,
    mostrar_stats,
    pedir_continuar,
)

from app.app import HelpApp
from app.catalogo import CatalogoMensagens
from app.mensagens import MensagemCatalogo
from app.dominio import EntradaSessao
from app.pipeline import PipelineCompleto
from app.persistence import PersistenciaMemoria
from app.historico import Historico

from app.perfil_store import PerfilStoreJSON
from app.aprendizagem import AprendizagemBasica


def resource_path(relative_path: str) -> Path:
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS) / relative_path
    return Path(__file__).resolve().parent / relative_path


def intensidade_auto(perfil, estado: str) -> int:
    """
    Começa em 3.0.
    Se for um novo dia e o estado repetir, soma +0.25.
    Quando atingir 4.00, passa a usar frases de intensidade 4 (bucket int()).
    """
    hoje = date.today().isoformat()

    # cria o dicionário se ainda não existir no perfil
    if not hasattr(perfil, "intensidades") or perfil.intensidades is None:
        perfil.intensidades = {}

    info = perfil.intensidades.get(estado)

    if not info:
        perfil.intensidades[estado] = {"valor": 3.0, "ultima_data": hoje}
        return 3

    if hoje > info.get("ultima_data", ""):
        info["valor"] = min(5.0, float(info.get("valor", 3.0)) + 0.25)
        info["ultima_data"] = hoje

    bucket = int(info["valor"])
    return max(1, min(5, bucket))


def main():
    # paths
    base = Path(__file__).resolve().parent
    mensagens_path = base / "data" / "mensagens.json"
    perfis_dir = base / "data" / "perfis"

    # infra
    catalogo = CatalogoMensagens(mensagens_path)
    msg = MensagemCatalogo(catalogo)

    pipeline = PipelineCompleto(logger=None)
    historico = Historico(PersistenciaMemoria())
    app = HelpApp(pipeline, historico)

    store = PerfilStoreJSON(perfis_dir)
    aprendizagem = AprendizagemBasica()

    # UI
    cabecalho()

    # utilizador
    nome = input("Nome do utilizador: ").strip()  # (se quiseres também posso trocar isto para rich Prompt)
    perfil = store.carregar(nome)

    # estados disponíveis: vamos buscar do catálogo
    # ADICIONA NO CatalogoMensagens: def estados(self): return sorted(self._data.keys())
    estados_disponiveis = catalogo.estados()

    # loop
    while True:
        estado = pedir_estado(estados_disponiveis, default=estados_disponiveis[0])

        intensidade = intensidade_auto(perfil, estado)

        entrada = EntradaSessao(
            estado=estado,
            intensidade=intensidade,
            utilizador=perfil.nome
        )

        texto = app.correr_sessao(msg, entrada)

        # aprendizagem + persistência do perfil
        aprendizagem.atualizar(perfil, entrada)
        store.guardar(perfil)

        mostrar_resposta(estado, intensidade, texto, data=getattr(entrada, "data", None))

        mostrar_stats(
            total_sessoes=perfil.total_sessoes,
            estado=estado,
            contagem_estado=perfil.contagem_estados.get(estado, 0),
            media_intensidade=perfil.media_intensidade(estado),
        )

        if not pedir_continuar():
            break

    mostrar_historico(app.ver_historico(5), titulo="Histórico (últimas 5)")


if __name__ == "__main__":
    main()
