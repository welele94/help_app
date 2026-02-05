# ui/rich_ui.py
from __future__ import annotations

from typing import Any, Iterable, Optional, Sequence

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.text import Text

console = Console()


# -------------------------
# Helpers (não mexer)
# -------------------------
def _get(obj: Any, *names: str, default: Any = "") -> Any:
    """
    Lê atributo OU chave de dicionário.
    Tenta vários nomes e devolve o primeiro que existir.
    """
    if obj is None:
        return default

    # dict-like
    if isinstance(obj, dict):
        for n in names:
            if n in obj:
                return obj.get(n, default)
        return default

    # object-like
    for n in names:
        if hasattr(obj, n):
            return getattr(obj, n)
    return default


def _safe_str(x: Any) -> str:
    return "" if x is None else str(x)


# -------------------------
# UI básica
# -------------------------
def mostrar_cabecalho(titulo: str = "Help!", subtitulo: str = "A tua app de estados de espírito") -> None:
    text = Text()
    text.append(titulo, style="bold cyan")
    text.append("\n")
    text.append(subtitulo, style="dim")
    console.print(Panel(text, border_style="cyan", expand=False))


def mostrar_info(msg: str) -> None:
    console.print(f"[cyan]ℹ[/cyan] {_safe_str(msg)}")


def mostrar_sucesso(msg: str) -> None:
    console.print(f"[green]✅[/green] {_safe_str(msg)}")


def mostrar_aviso(msg: str) -> None:
    console.print(f"[yellow]⚠[/yellow] {_safe_str(msg)}")


def mostrar_erro(msg: str) -> None:
    console.print(f"[bold red]✖[/bold red] {_safe_str(msg)}")


# -------------------------
# Inputs (Prompt)
# -------------------------
def pedir_nome(default: str = "utilizador") -> str:
    nome = Prompt.ask("Nome do utilizador", default=default).strip()
    return nome or default


def pedir_estado(estados: Sequence[str], default: Optional[str] = None) -> str:
    """
    Pede o estado ao utilizador com choices (evita typos).
    """
    if not estados:
        # fallback: sem choices
        estado = Prompt.ask("Como te sentes hoje? (estado)").strip()
        return estado

    if default is None:
        default = estados[0]

    estado = Prompt.ask(
        "Como te sentes hoje?",
        choices=list(estados),
        default=default,
        show_choices=True,
    ).strip()
    return estado


def confirmar(pergunta: str, default: bool = True) -> bool:
    return Confirm.ask(pergunta, default=default)


# -------------------------
# Outputs principais
# -------------------------
def mostrar_mensagem_final(
    estado: str,
    intensidade: int,
    frase: str,
    titulo: str = "Mensagem do dia",
) -> None:
    """
    Mostra estado + intensidade + frase num Panel.
    """
    corpo = (
        f"[bold]Estado:[/bold] {estado}\n"
        f"[bold]Intensidade:[/bold] {intensidade}/5\n\n"
        f"{frase}"
    )
    console.print(Panel(corpo, title=titulo, border_style="magenta", expand=False))


def mostrar_resumo_sessao(entrada: Any, frase: str) -> None:
    """
    Se preferires passar a EntradaSessao inteira.
    Tenta apanhar nomes comuns:
      estado, intensidade, data/data_hora, utilizador/nome
    """
    estado = _safe_str(_get(entrada, "estado"))
    intensidade = _get(entrada, "intensidade", default=3)
    data = _safe_str(_get(entrada, "data", "data_hora", "timestamp", default=""))
    utilizador = _safe_str(_get(entrada, "utilizador", "nome", "username", default=""))

    header = f"[bold]Sessão[/bold]"
    if utilizador:
        header += f" — {utilizador}"
    if data:
        header += f" — {data}"

    corpo = (
        f"[bold]Estado:[/bold] {estado}\n"
        f"[bold]Intensidade:[/bold] {intensidade}/5\n\n"
        f"{frase}"
    )
    console.print(Panel(corpo, title=header, border_style="magenta", expand=False))


def mostrar_historico(entradas: Iterable[Any], titulo: str = "Histórico") -> None:
    """
    Mostra histórico numa tabela.
    Cada entrada pode ser objeto ou dict.
    Campos tentados:
      data/data_hora/timestamp | estado | intensidade | mensagem/frase/texto
    """
    table = Table(title=titulo, show_lines=False)

    table.add_column("Data", style="dim", no_wrap=True)
    table.add_column("Estado", style="cyan")
    table.add_column("Int.", justify="center")
    table.add_column("Mensagem", overflow="fold")

    count = 0
    for e in entradas:
        count += 1
        data = _safe_str(_get(e, "data", "data_hora", "timestamp", default=""))
        estado = _safe_str(_get(e, "estado", default=""))
        intensidade = _safe_str(_get(e, "intensidade", default=""))
        msg = _safe_str(_get(e, "mensagem", "frase", "texto", default=""))

        table.add_row(data, estado, intensidade, msg)

    if count == 0:
        mostrar_aviso("Ainda não há histórico.")
        return

    console.print(table)


# -------------------------
# Pequenos utilitários úteis
# -------------------------
def mostrar_menu(opcoes: Sequence[str], titulo: str = "Menu", default: Optional[str] = None) -> str:
    """
    Menu simples: devolve a opção escolhida (string).
    """
    if not opcoes:
        raise ValueError("menu sem opções")

    if default is None:
        default = opcoes[0]

    console.print(Panel("\n".join(f"- {o}" for o in opcoes), title=titulo, border_style="blue", expand=False))
    escolha = Prompt.ask("Escolhe", choices=list(opcoes), default=default, show_choices=False)
    return escolha
