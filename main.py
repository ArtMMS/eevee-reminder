"""
main.py
Ponto de entrada da aplicacao — Fase 4: Horarios Configuraveis + Interface.

Deliverable da Fase 4: um sistema de lembretes controlado por um arquivo
de configuracao externo (config/reminders.json), com interface grafica
para adicionar/remover horarios sem editar o codigo.
"""

import queue
import threading
from pathlib import Path

import winsound

from config import carregar_lembretes, salvar_lembretes
from gui import criar_janela_principal, mostrar_popup
from scheduler import monitorar

PASTA_PROJETO = Path(__file__).resolve().parent
CAMINHO_SOM = PASTA_PROJETO / "assets" / "sounds" / "alert.wav"
INTERVALO_VERIFICACAO = 5

# lista compartilhada entre a interface (thread principal) e o monitor (thread de fundo)
lembretes = carregar_lembretes()
fila_lembretes: "queue.Queue[dict]" = queue.Queue()


def obter_lembretes_atuais() -> list[dict]:
    """Retorna uma copia da lista atual (chamada pela thread de monitoramento)."""
    return list(lembretes)


def adicionar_lembrete(nome: str, horario: str) -> None:
    lembretes.append({"nome": nome, "horario": horario})
    salvar_lembretes(lembretes)


def remover_lembrete(indice: int) -> None:
    lembretes.pop(indice)
    salvar_lembretes(lembretes)


def tocar_alerta() -> None:
    """
    Toca o som de alerta EM LOOP (SND_LOOP), repetindo continuamente
    ate ser parado explicitamente (por parar_alerta()).
    """
    if CAMINHO_SOM.exists():
        winsound.PlaySound(
            str(CAMINHO_SOM),
            winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_LOOP,
        )
    else:
        print(f"[aviso] arquivo de som nao encontrado em: {CAMINHO_SOM}")
        winsound.Beep(1000, 500)


def parar_alerta() -> None:
    winsound.PlaySound(None, winsound.SND_PURGE)


def lembrete_disparado(lembrete: dict) -> None:
    """Callback chamado pelo scheduler (na thread de monitoramento)."""
    tocar_alerta()
    fila_lembretes.put(lembrete)


def checar_fila(root) -> None:
    try:
        while True:
            lembrete = fila_lembretes.get_nowait()
            mensagem = f"{lembrete['nome']} — {lembrete['horario']}"
            mostrar_popup(root, mensagem, ao_confirmar=parar_alerta)
    except queue.Empty:
        pass

    root.after(500, checar_fila, root)


if __name__ == "__main__":
    print("=== Eevee Reminder — Fase 4 ===\n")

    thread_monitor = threading.Thread(
        target=monitorar,
        kwargs={
            "obter_lembretes": obter_lembretes_atuais,
            "ao_disparar": lembrete_disparado,
            "intervalo_segundos": INTERVALO_VERIFICACAO,
        },
        daemon=True,
    )
    thread_monitor.start()

    root, _tabela = criar_janela_principal(
        lembretes_iniciais=lembretes,
        ao_adicionar=adicionar_lembrete,
        ao_remover=remover_lembrete,
    )
    root.after(500, checar_fila, root)
    root.mainloop()