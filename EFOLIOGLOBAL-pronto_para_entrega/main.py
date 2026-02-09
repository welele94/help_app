from __future__ import annotations

from pathlib import Path
import sys

from ui.rich_ui import (
    mostrar_cabecalho,
    pedir_estado_com_emojis,
    mostrar_mensagem_final,
    mostrar_info,
    mostrar_aviso,
    mostrar_historico,
    confirmar,
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
from app.algoritmo_intensidade import calcular_intensidade


def resource_path(relative_path: str) -> Path:
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS) / relative_path
    return Path(__file__).resolve().parent / relative_path




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
    mostrar_cabecalho()

    # utilizador / input deve ficar com as primeiras letras de cada palavra em maiusculas
    raw_nome = input("Nome de Utilizador: ").strip().capitalize()

    # feedback UX (antes de carregar)
    if store.existe(raw_nome):
        mostrar_info(f"Bem-vindo de volta, {raw_nome}!")
    else:
        mostrar_info(f"Novo utilizador criado: {raw_nome}")

    # carrega (ou cria) o perfil real a partir de data/perfis
    perfil = store.carregar(raw_nome)

    # estados disponíveis vindos do mensagens.json
    estados_disponiveis = catalogo.estados()
    # menu 1-6 com emojis (só ficam os estados que existirem no JSON)
    opcoes = {
        "1": ("😟", "ansioso"),
        "2": ("😞", "triste"),
        "3": ("😤", "zangado"),
        "4": ("😴", "cansado"),
        "5": ("😌", "feliz"),
        "6": ("🔥", "motivado"),
    }

    opcoes = {k: v for k, v in opcoes.items() if v[1] in estados_disponiveis}

    # fallback caso o teu JSON tenha nomes diferentes e o filtro tenha removido tudo
    if not opcoes:
        mostrar_aviso("Não há estados do menu a bater com o mensagens.json. Verifica as keys do JSON.")
        return

    # loop
    while True:
        raw_estado = pedir_estado_com_emojis(opcoes, default=None)
        estado = raw_estado.strip().lower()

        # (opcional) se implementares catalogo.normalizar_estado, troca pela linha abaixo:
        # estado = catalogo.normalizar_estado(raw_estado)

        if estado not in estados_disponiveis:
            mostrar_aviso("Estado não reconhecido. Tenta novamente.")
            continue

        intensidade = calcular_intensidade(perfil, estado)

        entrada = EntradaSessao(
            estado=estado,
            intensidade=intensidade,
            utilizador=perfil.nome
        )

        texto = app.correr_sessao(msg, entrada)

        # aprendizagem + persistência do perfil
        aprendizagem.atualizar(perfil, entrada)
        store.guardar(perfil)

        # UI: mensagem
        mostrar_mensagem_final(estado, intensidade, texto)

        # UI: stats (não tens mostrar_stats no rich_ui.py)
        mostrar_info(
            f"Stats: total={perfil.total_sessoes}, "
            f"{estado}={perfil.contagem_estados.get(estado, 0)}, "
            f"média_int={perfil.media_intensidade(estado):.2f}"
        )

        if not confirmar("Queres continuar?"):
            break

    # estatísticas/histórico (opcional)
    if confirmar("Queres ver as estatísticas?"):
        mostrar_info(
            f"Stats: total={perfil.total_sessoes}, "
            f"média_global={sum(perfil.soma_intensidade.values())/max(1, perfil.total_sessoes):.2f}"
        )
        mostrar_historico(app.ver_historico(5), titulo="Histórico (últimas 5)")
    else:
        mostrar_info("Foi um gosto ajudar-te!")


if __name__ == "__main__":
    main()
