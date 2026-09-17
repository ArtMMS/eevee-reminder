"""
main.py
Ponto de entrada da aplicacao — Fase 9: Empacotamento em Executavel.

Deliverable: app completo, pronto para ser gerado como um unico .exe
com o PyInstaller, mantendo os dados de configuracao ao lado do executavel.
"""

import os
import queue
import threading

import winsound
from PIL import Image, ImageTk

import startup
from config import carregar_lembretes, salvar_lembretes
from gui import criar_janela_principal, mostrar_popup
from resources import pasta_recursos
from scheduler import monitorar
from tray import criar_icone_bandeja, iniciar_icone_em_thread

CAMINHO_SOM = pasta_recursos() / "assets" / "sounds" / "alert.wav"
CAMINHO_ICONE = pasta_recursos() / "assets" / "icon.png"
INTERVALO_VERIFICACAO = 5

lembretes = carregar_lembretes()
fila_lembretes: "queue.Queue[dict]" = queue.Queue()


def obter_lembretes_atuais() -> list[dict]:
    """Retorna uma copia da lista atual (chamada pela thread de monitoramento)."""
    return list(lembretes)


def adicionar_lembrete(nome: str, horario: str) -> None:
    lembretes.append({"nome": nome, "horario": horario})
    salvar_lembretes(lembretes)


def editar_lembrete(indice: int, nome: str, horario: str) -> None:
    lembretes[indice] = {"nome": nome, "horario": horario}
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


def minimizar_para_bandeja(root) -> None:
    """Chamado ao clicar no X da janela principal: esconde em vez de fechar."""
    root.withdraw()


def restaurar_janela(root) -> None:
    """Chamado pelo menu 'Abrir' da bandeja (ou duplo clique no icone)."""
    root.deiconify()
    root.lift()
    root.focus_force()


def encerrar_aplicativo(icone) -> None:
    """Chamado pelo menu 'Sair' da bandeja: encerra tudo de vez."""
    icone.stop()
    winsound.PlaySound(None, winsound.SND_PURGE)
    os._exit(0)


def alternar_iniciar_com_windows(ativo: bool) -> None:
    """Chamado ao marcar/desmarcar o checkbox na janela de configuracoes."""
    try:
        if ativo:
            startup.habilitar()
        else:
            startup.desabilitar()
    except OSError as erro:
        print(f"[erro] nao foi possivel alterar a inicializacao com o Windows: {erro}")


if __name__ == "__main__":
    print("=== Eevee Reminder — Fase 9 ===\n")

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
        ao_editar=editar_lembrete,
        ao_remover=remover_lembrete,
        obter_iniciar_com_windows=startup.esta_habilitado,
        ao_alternar_iniciar_com_windows=alternar_iniciar_com_windows,
    )

    if CAMINHO_ICONE.exists():
        root.icone_janela = ImageTk.PhotoImage(Image.open(CAMINHO_ICONE))
        root.iconphoto(True, root.icone_janela)
    else:
        print(f"[aviso] icone nao encontrado em: {CAMINHO_ICONE}")

    root.protocol("WM_DELETE_WINDOW", lambda: minimizar_para_bandeja(root))

    icone_bandeja = criar_icone_bandeja(
        ao_abrir=lambda: root.after(0, restaurar_janela, root),
        ao_sair=lambda: encerrar_aplicativo(icone_bandeja),
    )
    iniciar_icone_em_thread(icone_bandeja)

    root.after(500, checar_fila, root)
    root.mainloop()