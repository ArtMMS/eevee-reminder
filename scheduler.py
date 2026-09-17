"""
scheduler.py
Logica central de monitoramento de horario.
Fase 4: suporta multiplos horarios de lembrete simultaneamente.
"""

from __future__ import annotations

import time
from datetime import datetime
from typing import Callable, TypedDict


class Lembrete(TypedDict):
    nome: str
    horario: str  # formato "HH:MM"


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

    obter_lembretes:     funcao que retorna a lista atual de lembretes
                          (chamada a cada iteracao, para refletir mudancas
                          feitas na interface em tempo real)
    ao_disparar:         funcao chamada quando um lembrete e atingido
    intervalo_segundos:  intervalo entre checagens do relogio
    """
    print("[scheduler] monitorando multiplos horarios...")
    print("Pressione Ctrl+C para encerrar.\n")

    ja_disparados: set[str] = set()  # chaves "nome|horario" ja disparadas neste minuto

    try:
        while True:
            agora_str = datetime.now().strftime("%H:%M:%S")
            lembretes_atuais = obter_lembretes()

            chaves_no_horario = set()

            for lembrete in lembretes_atuais:
                chave = f"{lembrete['nome']}|{lembrete['horario']}"

                if horario_atual_bate(lembrete["horario"]):
                    chaves_no_horario.add(chave)
                    if chave not in ja_disparados:
                        ao_disparar(lembrete)
                        ja_disparados.add(chave)

            # libera para disparar de novo no proximo dia, assim que o minuto passa
            ja_disparados = {c for c in ja_disparados if c in chaves_no_horario}

            print(f"[{agora_str}] monitorando {len(lembretes_atuais)} lembrete(s)...")
            time.sleep(intervalo_segundos)

    except KeyboardInterrupt:
        print("\nMonitoramento encerrado pelo usuario.")