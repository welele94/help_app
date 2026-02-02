from __future__ import annotations
from pathlib import Path
import sys

from help_app.app.app import HelpApp
from help_app.app.catalogo import CatalogoMensagens
from help_app.app.mensagens import MensagemCatalogo
from help_app.app.dominio import EntradaSessao
from help_app.app.pipeline import PipelineCompleto
from help_app.app.persistence import PersistenciaMemoria
from help_app.app.historico import Historico

from help_app.app.perfil_store import PerfilStoreJSON
from help_app.app.aprendizagem import AprendizagemBasica


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

    # utilizador: entra uma vez, fica persistido
    nome = input("Nome do utilizador: ").strip()
    perfil = store.carregar(nome)

    print(f"Bem-vindo, {perfil.nome}!")
    print("Escreve o teu estado (ex: ansioso/triste/zangado/cansado/motivado) e intensidade (1-5).")
    print("Escreve 'sair' para terminar.\n")

    while True:
        estado = input("Estado: ").strip().lower()
        if estado == "sair":
            break

        intensidade_str = input("Intensidade (1-5): ").strip()
        try:
            intensidade = max(1, min(5, int(intensidade_str)))
        except ValueError:
            print("Intensidade inválida. Usa um número 1-5.\n")
            continue

        entrada = EntradaSessao(estado=estado, intensidade=intensidade, utilizador=perfil.nome)

        texto = app.correr_sessao(msg, entrada)

        # aprendizagem + persistência do perfil
        aprendizagem.atualizar(perfil, entrada)
        store.guardar(perfil)

        print("\nResposta:", texto)
        print(f"Stats: total={perfil.total_sessoes}, {estado}={perfil.contagem_estados.get(estado, 0)}, "
              f"média_int={perfil.media_intensidade(estado):.2f}\n")

    print("\nAté já!")
    print("Histórico (últimas 5):", app.ver_historico(5))


if __name__ == "__main__":
    main()

def resource_path(relative_path: str) -> Path:
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIAPASS) / relative_path
    return Path(__file__).resolve().parent / relative_path