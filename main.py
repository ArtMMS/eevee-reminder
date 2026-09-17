"""
main.py
Ponto de entrada da aplicacao — Fase 9: Empacotamento em Executavel.

Deliverable: app completo, pronto para ser gerado como um unico .exe
com o PyInstaller, mantendo os dados de configuracao ao lado do executavel.
"""

import os
import queue
import socket
import sys
import threading
from datetime import datetime, timedelta

import winsound
from PIL import Image, ImageTk

import startup
from config import carregar_lembretes, salvar_lembretes
from gui import criar_janela_principal, mostrar_popup
from resources import pasta_recursos
from scheduler import monitorar
from tray import criar_icone_bandeja, iniciar_icone_em_thread

# Configuração de Instância Única
PORTA_SINGLE_INSTANCE = 65432  # Porta local para comunicação entre instâncias
CAMINHO_SOM = pasta_recursos() / "assets" / "sounds" / "alert.wav"
CAMINHO_ICONE = pasta_recursos() / "assets" / "icon.png"
INTERVALO_VERIFICACAO = 5

lembretes = carregar_lembretes()
fila_lembretes: "queue.Queue[dict]" = queue.Queue()
tabela_gui = None  # Referência global para atualizar a Treeview no Snooze


def verificar_instancia_unica() -> bool:
    """
    Tenta se conectar à porta do app. Se conseguir, avisa a primeira
    instância para restaurar a janela e encerra este processo (retorna False).
    """
    try:
        cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        cliente.connect(("127.0.0.1", PORTA_SINGLE_INSTANCE))
        cliente.sendall(b"RESTORE")
        cliente.close()
        return False
    except OSError:
        return True


def escutar_outras_instancias(root) -> None:
    """Servidor TCP em background que aguarda tentativas de abertura secundárias."""
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        servidor.bind(("127.0.0.1", PORTA_SINGLE_INSTANCE))
        servidor.listen(5)
    except OSError:
        return

    while True:
        try:
            conn, _ = servidor.accept()
            msg = conn.recv(1024)
            if msg == b"RESTORE":
                root.after(0, lambda: restaurar_janela(root))
            conn.close()
        except Exception:
            break


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


def adiar_lembrete(lembrete: dict, minutos: int = 5) -> None:
    """Atualiza o horário do lembrete existente em vez de criar um novo."""
    agora = datetime.now()
    novo_horario = (agora + timedelta(minutes=minutos)).strftime("%H:%M")
    
    # Procura o índice do lembrete original na lista
    indice_encontrado = None
    for i, item in enumerate(lembretes):
        if item["nome"] == lembrete["nome"] and item["horario"] == lembrete["horario"]:
            indice_encontrado = i
            break

    # Se encontrou, edita o existente; caso contrário, adiciona
    if indice_encontrado is not None:
        editar_lembrete(indice_encontrado, lembrete["nome"], novo_horario)
        
        # Atualiza a linha existente na Treeview (interface visual)
        if tabela_gui:
            children = tabela_gui.get_children()
            if indice_encontrado < len(children):
                item_id = children[indice_encontrado]
                tabela_gui.item(item_id, values=(lembrete["nome"], novo_horario))
    else:
        # Fallback de segurança se o item não estiver na lista
        adicionar_lembrete(lembrete["nome"], novo_horario)
        if tabela_gui:
            tabela_gui.insert("", "end", values=(lembrete["nome"], novo_horario))


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
            mostrar_popup(
                root, 
                mensagem, 
                ao_confirmar=parar_alerta,
                ao_adiar=lambda l=lembrete: adiar_lembrete(l, minutos=5)
            )
    except queue.Empty:
        pass

    root.after(500, checar_fila, root)


def minimizar_para_bandeja(root) -> None:
    """Chamado ao clicar no X da janela principal: esconde em vez de fechar."""
    root.withdraw()


def restaurar_janela(root) -> None:
    """Chamado pelo menu 'Abrir' da bandeja ou por nova tentativa de execução."""
    root.deiconify()
    root.state("normal")
    root.lift()
    root.attributes("-topmost", True)
    root.attributes("-topmost", False)
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
    if not verificar_instancia_unica():
        sys.exit(0)

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

    root, tabela_gui = criar_janela_principal(
        lembretes_iniciais=lembretes,
        ao_adicionar=adicionar_lembrete,
        ao_editar=editar_lembrete,
        ao_remover=remover_lembrete,
        obter_iniciar_com_windows=startup.esta_habilitado,
        ao_alternar_iniciar_com_windows=alternar_iniciar_com_windows,
    )

    thread_servidor = threading.Thread(
        target=escutar_outras_instancias,
        args=(root,),
        daemon=True,
    )
    thread_servidor.start()

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