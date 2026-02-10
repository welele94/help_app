# ui/rich_ui.py
from __future__ import annotations

from typing import Any, Iterable, Optional, Sequence

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.text import Text
from rich.align import Align


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
def mostrar_cabecalho(titulo: str = "Help!", subtitulo: str = "A sua app de estados de espírito") -> None:
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
    nome = Prompt.ask("Olá! Qual o seu nome?", default=default).strip()
    return nome or default


def pedir_estado_com_emojis(
    mapa_opcoes: dict[str, tuple[str, str]],
    default: str = "1",
    titulo: str = "Escolha o seu estado"
) -> str:
    """
    Menu numérico com emojis.
    mapa_opcoes exemplo:
      {
        "1": ("😟", "ansioso"),
        "2": ("😞", "triste"),
        ...
      }

    Retorna o estado (ex: "ansioso").
    """
    # layout em 2 colunas (3+3)
    items = [(k, v[0], v[1]) for k, v in sorted(mapa_opcoes.items(), key=lambda x: int(x[0]))]
    meio = (len(items) + 1) // 2
    esquerda = items[:meio]
    direita = items[meio:]

    tabela = Table(show_header=False, box=None, pad_edge=False)
    tabela.add_column(justify="left", no_wrap=True)
    tabela.add_column(justify="left", no_wrap=True)

    for i in range(meio):
        e = esquerda[i] if i < len(esquerda) else ("", "", "")
        d = direita[i] if i < len(direita) else ("", "", "")
        left = f"[bold]{e[0]}[/bold]  {e[1]}  {e[2]}" if e[0] else ""
        right = f"[bold]{d[0]}[/bold]  {d[1]}  {d[2]}" if d[0] else ""
        tabela.add_row(left, right)

    console.print(Panel(tabela, title=titulo, border_style="cyan", expand=False))

    escolha = Prompt.ask("Escolha (1-6)", choices=list(mapa_opcoes.keys()), default=default, show_choices=False)
    return mapa_opcoes[escolha][1]


# fallback para texto livre, caso queiras manter
def pedir_estado_texto(default: str = "") -> str:
    estado = Prompt.ask("Escreva o estado", default=default).strip()
    return estado


def confirmar(pergunta: str) -> bool:
    resp = Prompt.ask(
        f"{pergunta} [s/n]",
        choices=["s", "n"],
        show_choices=True,
    )
    return resp == "s"


# -------------------------
# Outputs principais
# -------------------------

def mostrar_mensagem_final(
    estado: str,
    intensidade: int,
    frase: str,
    titulo: str = "Mensagem do dia",
) -> None:
    # “aumentar” o texto duplicando linhas + espaçamento
    frase_grande = "\n\n".join([frase.upper()])

    corpo = Text()
    corpo.append(f"Estado: {estado}\n", style="bold cyan")
    corpo.append(f"Intensidade: {intensidade}/5\n\n", style="dim")
    corpo.append(frase_grande, style="bold white")

    painel = Panel(
        Align.center(corpo),
        title=f"💬 {titulo}",
        border_style="magenta",
        padding=(2, 4),
        width=70,
    )

    console.print(painel)


def mostrar_resumo_sessao(entrada: Any, frase: str) -> None:
    """
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
