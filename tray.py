"""
tray.py
Icone na bandeja do sistema (system tray) — Fase 9.
Usa pasta_recursos() para localizar o icone tanto rodando como script
quanto empacotado como executavel (.exe).
"""

import threading
from typing import Callable

import pystray
from PIL import Image

from resources import pasta_recursos


def criar_icone_bandeja(
    ao_abrir: Callable[[], None],
    ao_sair: Callable[[], None],
) -> pystray.Icon:
    """
    Cria o icone da bandeja com um menu de contexto:
    - "Abrir Eevee Reminder": mostra a janela principal (tambem e o item
      padrao, entao um duplo clique no icone ja aciona isso)
    - "Sair": encerra o aplicativo por completo
    """
    caminho_icone = pasta_recursos() / "assets" / "icon.png"

    if caminho_icone.exists():
        imagem = Image.open(caminho_icone)
    else:
        imagem = Image.new("RGB", (64, 64), color=(222, 184, 135))

    menu = pystray.Menu(
        pystray.MenuItem(
            "Abrir Eevee Reminder",
            lambda icon, item: ao_abrir(),
            default=True,
        ),
        pystray.MenuItem("Sair", lambda icon, item: ao_sair()),
    )

    return pystray.Icon("eevee_reminder", imagem, "Eevee Reminder", menu)


def iniciar_icone_em_thread(icone: pystray.Icon) -> threading.Thread:
    """Roda o icone da bandeja numa thread separada (nao bloqueia o Tkinter)."""
    thread = threading.Thread(target=icone.run, daemon=True)
    thread.start()
    return thread