"""
scheduler.py
Logica central de monitoramento de horario.
Fase 4: suporta multiplos horarios de lembrete simultaneamente.
Fase 10: pula lembretes marcados como inativos ("ativo": False).
"""

from __future__ import annotations

import time
from datetime import datetime
from typing import Callable, TypedDict


class Lembrete(TypedDict):
    nome: str
    horario: str  # formato "HH:MM"
    ativo: bool   # opcional na pratica; ausencia e tratada como True


def horario_atual_bate(horario_alvo: str) -> bool:
    agora = datetime.now().strftime("%H:%M")
    return agora == horario_alvo


def monitorar(
    obter_lembretes: Callable[[], list[Lembrete]],
    ao_disparar: Callable[[Lembrete], None],
    intervalo_segundos: int = 5,
) -> None:
    """
    Loop de monitoramento do relogio do sistema, suportando varios lembretes.
    Lembretes com "ativo": False sao ignorados (nao disparam alerta).
    """
    print("[scheduler] monitorando multiplos horarios...")
    print("Pressione Ctrl+C para encerrar.\n")

    ja_disparados: set[str] = set()

    try:
        while True:
            agora_str = datetime.now().strftime("%H:%M:%S")
            lembretes_atuais = obter_lembretes()

            chaves_no_horario = set()

            for lembrete in lembretes_atuais:
                if not lembrete.get("ativo", True):
                    continue  # lembrete desativado pelo usuario, ignora

                chave = f"{lembrete['nome']}|{lembrete['horario']}"

                if horario_atual_bate(lembrete["horario"]):
                    chaves_no_horario.add(chave)
                    if chave not in ja_disparados:
                        ao_disparar(lembrete)
                        ja_disparados.add(chave)

            ja_disparados = {c for c in ja_disparados if c in chaves_no_horario}

            print(f"[{agora_str}] monitorando {len(lembretes_atuais)} lembrete(s)...")
            time.sleep(intervalo_segundos)

    except KeyboardInterrupt:
        print("\nMonitoramento encerrado pelo usuario.")