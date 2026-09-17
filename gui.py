"""
gui.py
Modern GUI (Tkinter / Custom Cards) with Pastel theme, custom window layout, and Eevee mascot.
Integrated PNG Assets: eevee1, eevee2, clock, event, home, setting, sun, half-moon, pill.
Includes keyboard selection, DEL key item removal functionality, and enlarged Eevee mascot.
"""

import ctypes
import os
import tkinter as tk
from datetime import datetime
from tkinter import messagebox, ttk
from typing import Callable, Optional, TypedDict

from PIL import Image, ImageTk
from resources import pasta_recursos

# ----------------------------------------------------------------------
# GLOBAL COLOR PALETTE & CONFIG
# ----------------------------------------------------------------------
BG_MAIN = "#FAF6F0"          # Light Cream
BG_SIDEBAR = "#F5EBE1"       # Soft Cream (Sidebar)
BG_CARD = "#FFFFFF"          # White Card Background
BG_CARD_SELECTED = "#F5EBE1" # Card Highlight on Select
BG_HIGHLIGHT = "#EAF4EC"     # Pastel Green
BG_SELECTION = "#E8DCCE"     # Selection Highlight
ACCENT_PRIMARY = "#8B5A2B"   # Terracotta / Brown
TEXT_COLOR = "#2C2C2C"        # Main Text
TEXT_MUTED = "#7D7D7D"       # Subtitles / Muted

# Paleta de círculos coloridos pastéis para os ícones
CORES_CIRCULOS = ["#E3F2FD", "#F3E5F5", "#FFEBEE", "#E8F5E9"]


class Lembrete(TypedDict):
    nome: str
    horario: str


def carregar_icone(nome_arquivo: str, tamanho: tuple[int, int]) -> Optional[ImageTk.PhotoImage]:
    """Loads PNG images from assets directory with custom dimensions."""
    caminho = pasta_recursos() / "assets" / nome_arquivo
    if caminho.exists():
        img = Image.open(caminho).convert("RGBA")
        img = img.resize(tamanho, Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(img)
    return None


def obter_saudacao() -> tuple[str, str]:
    """Returns 'Welcome back!' alongside the sun or moon icon based on current system time."""
    hora = datetime.now().hour
    if 6 <= hora < 18:
        return "Welcome back!", "sun.png"
    return "Welcome back!", "half-moon.png"


def aplicar_cantos_arredondados_windows(root: tk.Tk):
    """Aplica cantos arredondados nativos no Windows 11/10 via DWM."""
    try:
        DWMWA_WINDOW_CORNER_PREFERENCE = 33
        DWMWCP_ROUND = 2
        hwnd = ctypes.windll.user32.GetParent(root.winfo_id())
        if hwnd == 0:
            hwnd = root.winfo_id()
        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            hwnd,
            DWMWA_WINDOW_CORNER_PREFERENCE,
            ctypes.byref(ctypes.c_int(DWMWCP_ROUND)),
            ctypes.sizeof(ctypes.c_int),
        )
    except Exception:
        pass


def criar_botao_arredondado(parent, text, command, bg_color=ACCENT_PRIMARY, fg_color="white", width=130, height=34, radius=12):
    """Generates a smooth rounded button using native Tkinter Canvas."""
    canvas = tk.Canvas(parent, width=width, height=height, bg=parent["bg"], highlightthickness=0, cursor="hand2")

    r = radius
    canvas.create_arc((0, 0, 2 * r, 2 * r), start=90, extent=90, fill=bg_color, outline=bg_color)
    canvas.create_arc((width - 2 * r, 0, width, 2 * r), start=0, extent=90, fill=bg_color, outline=bg_color)
    canvas.create_arc((0, height - 2 * r, 2 * r, height), start=180, extent=90, fill=bg_color, outline=bg_color)
    canvas.create_arc((width - 2 * r, height - 2 * r, width, height), start=270, extent=90, fill=bg_color, outline=bg_color)
    canvas.create_rectangle((r, 0, width - r, height), fill=bg_color, outline=bg_color)
    canvas.create_rectangle((0, r, width, height - r), fill=bg_color, outline=bg_color)

    canvas.create_text(width / 2, height / 2, text=text, fill=fg_color, font=("Segoe UI", 9, "bold"))
    canvas.bind("<Button-1>", lambda _e: command())
    return canvas


def calcular_proximo_lembrete(lembretes: list[Lembrete]) -> Optional[tuple[dict, str]]:
    """Calculates the upcoming reminder and precise time remaining (hours, minutes, seconds)."""
    if not lembretes:
        return None

    agora = datetime.now()
    proximos = []

    for item in lembretes:
        try:
            h, m = map(int, item["horario"].split(":"))
            dt_alvo = agora.replace(hour=h, minute=m, second=0, microsecond=0)
            if dt_alvo < agora:
                dt_alvo = dt_alvo.replace(day=agora.day + 1)

            diferenca = dt_alvo - agora
            proximos.append((diferenca.total_seconds(), item, dt_alvo))
        except ValueError:
            continue

    if not proximos:
        return None

    proximos.sort(key=lambda x: x[0])
    segundos_totais = int(proximos[0][0])
    item_proximo = proximos[0][1]

    horas = segundos_totais // 3600
    minutos = (segundos_totais % 3600) // 60
    segundos = segundos_totais % 60

    partes = []
    if horas > 0:
        partes.append(f"{horas}h")
    if minutos > 0 or horas > 0:
        partes.append(f"{minutos}m")
    partes.append(f"{segundos}s")

    tempo_str = "in " + " ".join(partes)
    return item_proximo, tempo_str


def criar_janela_principal(
    lembretes_iniciais: list[Lembrete],
    ao_adicionar: Callable[[str, str], None],
    ao_editar: Callable[[int, str, str], None],
    ao_remover: Callable[[int], None],
    obter_iniciar_com_windows: Callable[[], bool],
    ao_alternar_iniciar_com_windows: Callable[[bool], None],
) -> tuple[tk.Tk, object]:

    root = tk.Tk()
    root.title("Eevee Reminder")
    root.geometry("850x580")
    root.resizable(False, False)
    root.configure(bg=BG_MAIN)

    root.update()
    aplicar_cantos_arredondados_windows(root)

    imagens_referencia = {}

    # Pré-carregar ícone da pílula
    img_pill = carregar_icone("pill.png", (20, 20))
    if img_pill:
        imagens_referencia["pill"] = img_pill

    # Controle de seleção atual
    indice_selecionado: Optional[int] = None
    widgets_linhas: list[dict] = []

    # ------------------------------------------------------------------
    # SIDEBAR (Aumentada para 240px para acomodar o Eevee maior)
    # ------------------------------------------------------------------
    sidebar = tk.Frame(root, bg=BG_SIDEBAR, width=240)
    sidebar.pack(side="left", fill="y")
    sidebar.pack_propagate(False)

    tk.Frame(sidebar, bg=BG_SIDEBAR, height=15).pack(fill="x")

    def criar_btn_sidebar(texto: str, nome_img: str, comando=None, ativo=False):
        cor_bg = BG_SELECTION if ativo else BG_SIDEBAR
        frame_btn = tk.Frame(sidebar, bg=cor_bg)
        frame_btn.pack(fill="x", padx=10, pady=3)

        img_icon = carregar_icone(nome_img, (18, 18))
        if img_icon:
            imagens_referencia[f"btn_{texto}"] = img_icon
            lbl = tk.Label(frame_btn, image=img_icon, bg=cor_bg)
            lbl.pack(side="left", padx=(12, 8), pady=8)

        btn = tk.Button(
            frame_btn,
            text=texto,
            font=("Segoe UI", 10, "bold" if ativo else "normal"),
            bg=cor_bg,
            fg=ACCENT_PRIMARY if ativo else TEXT_COLOR,
            anchor="w",
            bd=0,
            activebackground=BG_SELECTION,
            command=comando,
        )
        btn.pack(side="left", fill="x", expand=True)

    criar_btn_sidebar("Home", "home.png", ativo=True)
    criar_btn_sidebar(
        "Settings",
        "setting.png",
        comando=lambda: abrir_janela_configuracoes(root, obter_iniciar_com_windows, ao_alternar_iniciar_com_windows),
    )

    frame_mascot_container = tk.Frame(sidebar, bg=BG_SIDEBAR)
    frame_mascot_container.pack(side="bottom", pady=(0, 15))

    # Eevee aumentado para 180x180 pixels
    img_eevee_main = carregar_icone("eevee1.png", (200, 200))
    if img_eevee_main:
        imagens_referencia["eevee_main"] = img_eevee_main
        lbl_eevee = tk.Label(frame_mascot_container, image=img_eevee_main, bg=BG_SIDEBAR)
        lbl_eevee.pack(pady=(0, 4))

    tk.Label(
        frame_mascot_container,
        text="Small steps\nfor a healthier you! ♥",
        font=("Segoe UI", 8, "bold"),
        bg=BG_SIDEBAR,
        fg=TEXT_MUTED,
        justify="center",
    ).pack()

    # ------------------------------------------------------------------
    # MAIN PANEL
    # ------------------------------------------------------------------
    main_panel = tk.Frame(root, bg=BG_MAIN, padx=25, pady=20)
    main_panel.pack(side="right", fill="both", expand=True)

    saudacao_texto, icone_saudacao = obter_saudacao()
    frame_saudacao = tk.Frame(main_panel, bg=BG_MAIN)
    frame_saudacao.pack(anchor="w")

    tk.Label(frame_saudacao, text=saudacao_texto, font=("Segoe UI", 18, "bold"), bg=BG_MAIN, fg=TEXT_COLOR).pack(side="left")

    img_sol_lua = carregar_icone(icone_saudacao, (24, 24))
    if img_sol_lua:
        imagens_referencia["saudacao"] = img_sol_lua
        lbl_sol = tk.Label(frame_saudacao, image=img_sol_lua, bg=BG_MAIN)
        lbl_sol.pack(side="left", padx=8)

    tk.Label(main_panel, text="Here are your medication reminders.", font=("Segoe UI", 10), bg=BG_MAIN, fg=TEXT_MUTED).pack(
        anchor="w", pady=(0, 12)
    )

    # ------------------------------------------------------------------
    # CLEAN SCHEDULE CARD CONTAINER
    # ------------------------------------------------------------------
    card_container = tk.Frame(main_panel, bg=BG_CARD, highlightthickness=1, highlightbackground="#EFEBE4")
    card_container.pack(fill="x", pady=(0, 12))

    # Cabeçalho do Card
    frame_topo_tabela = tk.Frame(card_container, bg=BG_CARD, padx=16, pady=12)
    frame_topo_tabela.pack(fill="x")

    img_event = carregar_icone("event.png", (20, 20))
    if img_event:
        imagens_referencia["event"] = img_event
        lbl_ev = tk.Label(frame_topo_tabela, image=img_event, bg=BG_CARD)
        lbl_ev.pack(side="left", padx=(0, 8))

    tk.Label(
        frame_topo_tabela,
        text="Today's Schedule",
        font=("Segoe UI", 11, "bold"),
        bg=BG_CARD,
        fg=TEXT_COLOR,
    ).pack(side="left")

    btn_add = criar_botao_arredondado(frame_topo_tabela, "+ Add Reminder", lambda: abrir_modal_formulario(), width=120, height=32)
    btn_add.pack(side="right")

    # Lista Interna dos Remédios
    frame_lista_remedios = tk.Frame(card_container, bg=BG_CARD, padx=16)
    frame_lista_remedios.pack(fill="x", pady=(0, 12))

    # Referência dinâmica para manter dados sincronizados
    lista_dados_lembretes = list(lembretes_iniciais)

    def atualizar_destaque_selecao():
        """Aplica estilo visual de seleção na linha atualmente focada."""
        nonlocal indice_selecionado
        for i, item_dict in enumerate(widgets_linhas):
            cor_bg = BG_CARD_SELECTED if i == indice_selecionado else BG_CARD
            row = item_dict["row"]
            row.config(bg=cor_bg)
            for child in item_dict["widgets"]:
                try:
                    child.config(bg=cor_bg)
                except tk.TclError:
                    pass

    def selecionar_item(indice: int):
        nonlocal indice_selecionado
        indice_selecionado = indice
        atualizar_destaque_selecao()
        root.focus_set()

    def deletar_item_selecionado():
        nonlocal indice_selecionado
        if indice_selecionado is not None and 0 <= indice_selecionado < len(lista_dados_lembretes):
            idx = indice_selecionado
            ao_remover(idx)
            lista_dados_lembretes.pop(idx)
            indice_selecionado = None
            recarregar_lista()

    def desenhar_item_remedio(nome: str, horario: str, indice: int):
        if len(frame_lista_remedios.winfo_children()) > 0:
            div = tk.Frame(frame_lista_remedios, bg="#F3EEE8", height=1)
            div.pack(fill="x", pady=6)

        item_row = tk.Frame(frame_lista_remedios, bg=BG_CARD, cursor="hand2")
        item_row.pack(fill="x", pady=2)

        # 1. Ícone em Círculo Pastel
        cor_fundo_circulo = CORES_CIRCULOS[indice % len(CORES_CIRCULOS)]
        canvas_icon = tk.Canvas(item_row, width=38, height=38, bg=BG_CARD, highlightthickness=0)
        canvas_icon.pack(side="left", padx=(0, 12))

        canvas_icon.create_oval(2, 2, 36, 36, fill=cor_fundo_circulo, outline=cor_fundo_circulo)
        if "pill" in imagens_referencia:
            canvas_icon.create_image(19, 19, image=imagens_referencia["pill"])

        # 2. Informações principais (Nome + Frequência)
        frame_info = tk.Frame(item_row, bg=BG_CARD)
        frame_info.pack(side="left", fill="y")

        lbl_nome = tk.Label(frame_info, text=nome, font=("Segoe UI", 10, "bold"), bg=BG_CARD, fg=TEXT_COLOR, anchor="w")
        lbl_nome.pack(fill="x")

        lbl_sub = tk.Label(frame_info, text="1 tablet • Daily", font=("Segoe UI", 8), bg=BG_CARD, fg=TEXT_MUTED, anchor="w")
        lbl_sub.pack(fill="x")

        # 3. Horário e Status
        frame_time = tk.Frame(item_row, bg=BG_CARD)
        frame_time.pack(side="right", padx=(10, 5))

        lbl_hora = tk.Label(frame_time, text=horario, font=("Segoe UI", 11, "bold"), bg=BG_CARD, fg=TEXT_COLOR, anchor="e")
        lbl_hora.pack(fill="x")

        lbl_status = tk.Label(frame_time, text="Scheduled", font=("Segoe UI", 8), bg=BG_CARD, fg=TEXT_MUTED, anchor="e")
        lbl_status.pack(fill="x")

        elementos = [item_row, canvas_icon, frame_info, lbl_nome, lbl_sub, frame_time, lbl_hora, lbl_status]
        widgets_linhas.append({"row": item_row, "widgets": elementos})

        # Menu Contextual (Editar / Deletar no botão direito)
        menu_ctx = tk.Menu(item_row, tearoff=0)
        menu_ctx.add_command(label="Edit", command=lambda: abrir_modal_formulario(indice))
        menu_ctx.add_command(
            label="Delete",
            command=lambda: (ao_remover(indice), lista_dados_lembretes.pop(indice), recarregar_lista()),
        )

        def exibir_menu(e):
            selecionar_item(indice)
            menu_ctx.tk_popup(e.x_root, e.y_root)

        # Eventos para interação e seleção
        for widget in elementos:
            widget.bind("<Button-1>", lambda _e, idx=indice: selecionar_item(idx))
            widget.bind("<Double-1>", lambda _e, idx=indice: abrir_modal_formulario(idx))
            widget.bind("<Button-3>", exibir_menu)

    def recarregar_lista():
        nonlocal widgets_linhas
        widgets_linhas.clear()
        for w in frame_lista_remedios.winfo_children():
            w.destroy()
        for idx, item in enumerate(lista_dados_lembretes):
            desenhar_item_remedio(item["nome"], item["horario"], idx)
        atualizar_destaque_selecao()

    recarregar_lista()

    # ------------------------------------------------------------------
    # ATALHOS DE TECLADO (DEL e ENTER)
    # ------------------------------------------------------------------
    def acao_tecla_delete(_event):
        deletar_item_selecionado()

    def acao_tecla_enter(_event):
        if indice_selecionado is not None and 0 <= indice_selecionado < len(lista_dados_lembretes):
            abrir_modal_formulario(indice_selecionado)

    root.bind("<Delete>", acao_tecla_delete)
    root.bind("<Return>", acao_tecla_enter)

    # ------------------------------------------------------------------
    # CARD "NEXT MEDICATION"
    # ------------------------------------------------------------------
    card_next = tk.Frame(main_panel, bg=BG_HIGHLIGHT, padx=15, pady=12, highlightthickness=1, highlightbackground="#D2E3D5")
    card_next.pack(fill="x")

    img_clock = carregar_icone("clock.png", (32, 32))
    if img_clock:
        imagens_referencia["clock"] = img_clock
        lbl_clk = tk.Label(card_next, image=img_clock, bg=BG_HIGHLIGHT)
        lbl_clk.pack(side="left", padx=(0, 12))

    frame_info_next = tk.Frame(card_next, bg=BG_HIGHLIGHT)
    frame_info_next.pack(side="left", fill="both")

    tk.Label(frame_info_next, text="Next Medication", font=("Segoe UI", 8, "bold"), bg=BG_HIGHLIGHT, fg=TEXT_MUTED).pack(
        anchor="w"
    )
    lbl_next_detalhe = tk.Label(
        frame_info_next, text="No scheduled reminders", font=("Segoe UI", 11, "bold"), bg=BG_HIGHLIGHT, fg=TEXT_COLOR
    )
    lbl_next_detalhe.pack(anchor="w")

    def atualizar_card_loop():
        res = calcular_proximo_lembrete(lista_dados_lembretes)
        if res:
            item, tempo = res
            lbl_next_detalhe.config(text=f"{item['horario']} — {item['nome']} ({tempo})")
        else:
            lbl_next_detalhe.config(text="No scheduled reminders")

        root.after(1000, atualizar_card_loop)

    atualizar_card_loop()

    # ------------------------------------------------------------------
    # MODAL FOR ADD / EDIT REMINDER
    # ------------------------------------------------------------------
    def abrir_modal_formulario(indice_edicao: Optional[int] = None):
        modal = tk.Toplevel(root)
        modal.title("Add Reminder" if indice_edicao is None else "Edit Reminder")
        modal.geometry("340x230")
        modal.configure(bg=BG_CARD)
        modal.resizable(False, False)
        modal.transient(root)
        modal.grab_set()

        modal.update()
        aplicar_cantos_arredondados_windows(modal)

        tk.Label(modal, text="Medication Details", font=("Segoe UI", 12, "bold"), bg=BG_CARD, fg=ACCENT_PRIMARY).pack(
            pady=(15, 10)
        )

        frame_campos = tk.Frame(modal, bg=BG_CARD, padx=20)
        frame_campos.pack(fill="x")

        tk.Label(frame_campos, text="Medication Name:", font=("Segoe UI", 9), bg=BG_CARD, fg=TEXT_MUTED).pack(anchor="w")
        ent_nome = tk.Entry(frame_campos, font=("Segoe UI", 10), bg=BG_MAIN, bd=1, relief="solid")
        ent_nome.pack(fill="x", pady=(2, 10))

        tk.Label(frame_campos, text="Time (HH:MM):", font=("Segoe UI", 9), bg=BG_CARD, fg=TEXT_MUTED).pack(anchor="w")
        ent_horario = tk.Entry(frame_campos, font=("Segoe UI", 10), bg=BG_MAIN, bd=1, relief="solid")
        ent_horario.pack(fill="x", pady=(2, 15))

        if indice_edicao is not None:
            item = lista_dados_lembretes[indice_edicao]
            ent_nome.insert(0, item["nome"])
            ent_horario.insert(0, item["horario"])

        def salvar():
            nonlocal indice_selecionado
            nome = ent_nome.get().strip()
            horario = ent_horario.get().strip()

            if not nome or not horario:
                messagebox.showwarning("Empty Fields", "Please fill in all fields.", parent=modal)
                return

            try:
                datetime.strptime(horario, "%H:%M")
            except ValueError:
                messagebox.showwarning("Invalid Time", "Use HH:MM format (e.g. 08:30).", parent=modal)
                return

            if indice_edicao is None:
                ao_adicionar(nome, horario)
                lista_dados_lembretes.append({"nome": nome, "horario": horario})
            else:
                ao_editar(indice_edicao, nome, horario)
                lista_dados_lembretes[indice_edicao] = {"nome": nome, "horario": horario}

            indice_selecionado = None
            recarregar_lista()
            modal.destroy()

        btn_modal = criar_botao_arredondado(modal, "Save", salvar, width=120, height=32)
        btn_modal.pack(pady=5)

    root.imagens_referencia = imagens_referencia
    return root, frame_lista_remedios


def abrir_janela_configuracoes(
    root: tk.Tk,
    obter_iniciar_com_windows: Callable[[], bool],
    ao_alternar_iniciar_com_windows: Callable[[bool], None],
) -> None:
    janela = tk.Toplevel(root)
    janela.title("Settings")
    janela.geometry("320x160")
    janela.resizable(False, False)
    janela.attributes("-topmost", True)

    janela.update()
    aplicar_cantos_arredondados_windows(janela)

    tk.Label(janela, text="Settings", font=("Segoe UI", 12, "bold")).pack(pady=(20, 15))

    var_win = tk.BooleanVar(value=obter_iniciar_com_windows())
    tk.Checkbutton(
        janela,
        text="Start automatically with Windows",
        variable=var_win,
        command=lambda: ao_alternar_iniciar_com_windows(var_win.get()),
    ).pack(padx=20, anchor="w")

    tk.Button(janela, text="Close", command=janela.destroy).pack(pady=(20, 0))


def mostrar_popup(
    root: tk.Tk,
    mensagem: str,
    ao_confirmar: Callable[[], None],
    ao_adiar: Optional[Callable[[], None]] = None,
) -> None:
    popup = tk.Toplevel(root)
    popup.title("Medication Reminder")
    popup.geometry("400x200")
    popup.resizable(False, False)
    popup.configure(bg="#FAF6F0")
    popup.attributes("-topmost", True)

    popup.update()
    aplicar_cantos_arredondados_windows(popup)

    popup.protocol("WM_DELETE_WINDOW", lambda: (ao_confirmar(), popup.destroy()))

    container = tk.Frame(popup, bg="#FAF6F0", padx=15, pady=15)
    container.pack(fill="both", expand=True)

    img_eevee = carregar_icone("eevee2.png", (140, 140))
    if not img_eevee:
        img_eevee = carregar_icone("eevee1.png", (140, 140))

    if img_eevee:
        lbl_img = tk.Label(container, image=img_eevee, bg="#FAF6F0")
        lbl_img.image = img_eevee
        lbl_img.pack(side="left", padx=(5, 15), anchor="c")

    frame_direito = tk.Frame(container, bg="#FAF6F0")
    frame_direito.pack(side="left", fill="both", expand=True)

    tk.Label(
        frame_direito,
        text="Next Medication",
        font=("Segoe UI", 14, "bold"),
        bg="#FAF6F0",
        fg="#1A1C2E",
        anchor="w",
    ).pack(fill="x", pady=(0, 2))

    tk.Label(
        frame_direito,
        text=mensagem,
        font=("Segoe UI", 9),
        bg="#FAF6F0",
        fg=TEXT_MUTED,
        anchor="w",
    ).pack(fill="x", pady=(0, 10))

    def acao_tomei():
        ao_confirmar()
        popup.destroy()

    def acao_adiar_popup():
        ao_confirmar()
        if ao_adiar:
            ao_adiar()
        popup.destroy()

    btn_confirm = criar_botao_arredondado(
        frame_direito,
        text="Confirm",
        command=acao_tomei,
        bg_color="#F5EBE1",
        fg_color="#1A1C2E",
        width=180,
        height=36,
        radius=10,
    )
    btn_confirm.pack(anchor="w", pady=(0, 6))

    if ao_adiar:
        btn_snooze = criar_botao_arredondado(
            frame_direito,
            text="Snooze 5 minutes",
            command=acao_adiar_popup,
            bg_color="#F5EBE1",
            fg_color="#1A1C2E",
            width=180,
            height=36,
            radius=10,
        )
        btn_snooze.pack(anchor="w")