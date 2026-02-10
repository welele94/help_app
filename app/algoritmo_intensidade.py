from __future__ import annotations

from typing import Any


def _bucket(valor: float) -> int:
    # bucket simples p/ escolher mensagens (sem stress)
    return max(1, min(5, int(valor)))


def _decair_outros(perfil: Any, estado_atual: str) -> None:
    """
    Quando se muda de estado, todos os outros perdem 0.25 até um mínimo de 0.0.
    """
    # isto ajuda a "esquecer" estados antigos de forma gradual
    for est, info in list(perfil.intensidades.items()):
        if est == estado_atual:
            continue
        valor = float(info.get("valor", 3.0))
        if valor > 0.0:
            info["valor"] = max(0.0, valor - 0.25)
            perfil.intensidades[est] = info


def calcular_intensidade(perfil: Any, estado: str) -> int:
    """
    Regras:
    - Mesmo estado consecutivo: multiplica por 1.25, depois 1.15, depois 1.05 (cap 5.0)
    - Mudou de estado: outros estados perdem 0.25 por sessão até mínimo 0.0
    - Ao mudar de estado: estado escolhido sobe ligeiramente (x1.05)
    """
    # inicializações seguras (não rebenta se o perfil for antigo)
    if not hasattr(perfil, "intensidades") or perfil.intensidades is None:
        perfil.intensidades = {}
    if not hasattr(perfil, "ultimo_estado"):
        perfil.ultimo_estado = None
    if not hasattr(perfil, "streak_estado"):
        perfil.streak_estado = 0

    if perfil.ultimo_estado != estado:
        # mudou de estado -> decay nos outros + boost leve no atual
        _decair_outros(perfil, estado)
        perfil.ultimo_estado = estado
        perfil.streak_estado = 1
        info = perfil.intensidades.get(estado, {"valor": 3.0})
        valor = max(0.0, float(info.get("valor", 3.0)))
        valor = min(5.0, valor * 1.05)
        info["valor"] = valor
        perfil.intensidades[estado] = info
        return _bucket(valor)

    # mesmo estado consecutivo -> agrava com multiplicadores em queda
    perfil.streak_estado += 1
    info = perfil.intensidades.get(estado, {"valor": 3.0})
    valor_atual = float(info.get("valor", 3.0))

    if perfil.streak_estado == 2:
        mult = 1.25
    elif perfil.streak_estado == 3:
        mult = 1.15
    else:
        mult = 1.05

    novo_valor = min(5.0, valor_atual * mult)
    info["valor"] = novo_valor
    perfil.intensidades[estado] = info

    return _bucket(novo_valor)
