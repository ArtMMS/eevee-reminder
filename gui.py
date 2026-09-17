"""
gui.py
Modern GUI (Tkinter / TTK) with Pastel theme and Eevee mascot.
Integrated PNG Assets: eevee1, clock, event, home, setting, sun, half-moon, pill.
"""

import os
import tkinter as tk
from datetime import datetime
from tkinter import messagebox, ttk
from typing import Callable, Optional, TypedDict

from PIL import Image, ImageTk
from resources import pasta_recursos

# ----------------------------------------------------------------------
# GLOBAL COLOR PALETTE (Eevee Pastel Theme)
# ----------------------------------------------------------------------
BG_MAIN = "#FAF6F0"       # Light Cream
BG_SIDEBAR = "#F5EBE1"    # Soft Cream (Sidebar)
BG_CARD = "#FFFFFF"       # White
BG_HIGHLIGHT = "#EAF4EC"  # Pastel Green
BG_SELECTION = "#E8DCCE"  # Selection Highlight
ACCENT_PRIMARY = "#8B5A2B" # Terracotta / Brown
TEXT_COLOR = "#2C2C2C"     # Main Text
TEXT_MUTED = "#7D7D7D"    # Subtitles / Muted


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


def criar_botao_arredondado(parent, text, command, bg_color=ACCENT_PRIMARY, fg_color="white", width=130, height=34, radius=12):
    """Generates a smooth rounded button using native Tkinter Canvas."""
    canvas = tk.Canvas(parent, width=width, height=height, bg=parent["bg"], highlightthickness=0, cursor="hand2")
    
    r = radius
    canvas.create_arc((0, 0, 2*r, 2*r), start=90, extent=90, fill=bg_color, outline=bg_color)
    canvas.create_arc((width-2*r, 0, width, 2*r), start=0, extent=90, fill=bg_color, outline=bg_color)
    canvas.create_arc((0, height-2*r, 2*r, height), start=180, extent=90, fill=bg_color, outline=bg_color)
    canvas.create_arc((width-2*r, height-2*r, width, height), start=270, extent=90, fill=bg_color, outline=bg_color)
    canvas.create_rectangle((r, 0, width-r, height), fill=bg_color, outline=bg_color)
    canvas.create_rectangle((0, r, width, height-r), fill=bg_color, outline=bg_color)

    canvas.create_text(width/2, height/2, text=text, fill=fg_color, font=("Segoe UI", 9, "bold"))
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
) -> tuple[tk.Tk, ttk.Treeview]:

    root = tk.Tk()
    root.title("Eevee Reminder")
    root.geometry("820x530")
    root.resizable(False, False)
    root.configure(bg=BG_MAIN)

    imagens_referencia = {}

    # TTK Flat Style
    style = ttk.Style(root)
    style.theme_use("clam")
    style.configure(
        "Treeview",
        background=BG_CARD,
        fieldbackground=BG_CARD,
        foreground=TEXT_COLOR,
        rowheight=38,
        font=("Segoe UI", 10),
        borderwidth=0,
        relief="flat",
    )
    style.configure(
        "Treeview.Heading",
        background=BG_MAIN,
        foreground=TEXT_MUTED,
        font=("Segoe UI", 8, "bold"),
        borderwidth=0,
        relief="flat",
    )
    style.map("Treeview", background=[("selected", BG_SELECTION)], foreground=[("selected", TEXT_COLOR)])

    # ------------------------------------------------------------------
    # SIDEBAR
    # ------------------------------------------------------------------
    sidebar = tk.Frame(root, bg=BG_SIDEBAR, width=210)
    sidebar.pack(side="left", fill="y")
    sidebar.pack_propagate(False)

    tk.Frame(sidebar, bg=BG_SIDEBAR, height=20).pack(fill="x")

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

    img_eevee_main = carregar_icone("eevee1.png", (140, 140))
    if img_eevee_main:
        imagens_referencia["eevee_main"] = img_eevee_main
        lbl_eevee = tk.Label(frame_mascot_container, image=img_eevee_main, bg=BG_SIDEBAR)
        lbl_eevee.pack(pady=(0, 6))

    tk.Label(
        frame_mascot_container,
        text="Small steps\nfor a healthier you! ♥",
        font=("Segoe UI", 8),
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

    tk.Label(main_panel, text="Here are your medication reminders.", font=("Segoe UI", 10), bg=BG_MAIN, fg=TEXT_MUTED).pack(anchor="w", pady=(0, 15))

    frame_topo_tabela = tk.Frame(main_panel, bg=BG_MAIN)
    frame_topo_tabela.pack(fill="x", pady=(0, 10))

    img_event = carregar_icone("event.png", (18, 18))
    if img_event:
        imagens_referencia["event"] = img_event
        lbl_ev = tk.Label(frame_topo_tabela, image=img_event, bg=BG_MAIN)
        lbl_ev.pack(side="left", padx=(0, 6))

    tk.Label(frame_topo_tabela, text="Today's Schedule", font=("Segoe UI", 11, "bold"), bg=BG_MAIN, fg=TEXT_COLOR).pack(side="left")

    # Table Setup (Column #0 for Pill Icon + Text)
    tabela = ttk.Treeview(main_panel, columns=("horario",), displaycolumns=("horario",), height=6)
    tabela.heading("#0", text="MEDICATION", anchor="w")
    tabela.heading("horario", text="TIME", anchor="center")
    tabela.column("#0", width=360, anchor="w")
    tabela.column("horario", width=120, anchor="center")
    tabela.pack(fill="x", pady=(0, 12))

    img_pill = carregar_icone("pill.png", (18, 18))
    if img_pill:
        imagens_referencia["pill"] = img_pill

    def inserir_item_tabela(nome: str, horario: str):
        kw = {"text": f"  {nome}", "values": (horario,)}
        if img_pill:
            kw["image"] = img_pill
        tabela.insert("", "end", **kw)

    for item in lembretes_iniciais:
        inserir_item_tabela(item["nome"], item["horario"])

    # Card "Next Medication"
    card_next = tk.Frame(main_panel, bg=BG_HIGHLIGHT, padx=15, pady=12, highlightthickness=1, highlightbackground="#D2E3D5")
    card_next.pack(fill="x")

    img_clock = carregar_icone("clock.png", (32, 32))
    if img_clock:
        imagens_referencia["clock"] = img_clock
        lbl_clk = tk.Label(card_next, image=img_clock, bg=BG_HIGHLIGHT)
        lbl_clk.pack(side="left", padx=(0, 12))

    frame_info_next = tk.Frame(card_next, bg=BG_HIGHLIGHT)
    frame_info_next.pack(side="left", fill="both")

    tk.Label(frame_info_next, text="Next Medication", font=("Segoe UI", 8, "bold"), bg=BG_HIGHLIGHT, fg=TEXT_MUTED).pack(anchor="w")
    lbl_next_detalhe = tk.Label(frame_info_next, text="No scheduled reminders", font=("Segoe UI", 11, "bold"), bg=BG_HIGHLIGHT, fg=TEXT_COLOR)
    lbl_next_detalhe.pack(anchor="w")

    # Real-time ticking update loop (Every 1000ms / 1 sec)
    def atualizar_card_loop():
        lembretes_atuais = [
            {"nome": tabela.item(c)["text"].strip(), "horario": tabela.item(c)["values"][0]}
            for c in tabela.get_children()
        ]
        res = calcular_proximo_lembrete(lembretes_atuais)
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

        tk.Label(modal, text="Medication Details", font=("Segoe UI", 12, "bold"), bg=BG_CARD, fg=ACCENT_PRIMARY).pack(pady=(15, 10))

        frame_campos = tk.Frame(modal, bg=BG_CARD, padx=20)
        frame_campos.pack(fill="x")

        tk.Label(frame_campos, text="Medication Name:", font=("Segoe UI", 9), bg=BG_CARD, fg=TEXT_MUTED).pack(anchor="w")
        ent_nome = tk.Entry(frame_campos, font=("Segoe UI", 10), bg=BG_MAIN, bd=1, relief="solid")
        ent_nome.pack(fill="x", pady=(2, 10))

        tk.Label(frame_campos, text="Time (HH:MM):", font=("Segoe UI", 9), bg=BG_CARD, fg=TEXT_MUTED).pack(anchor="w")
        ent_horario = tk.Entry(frame_campos, font=("Segoe UI", 10), bg=BG_MAIN, bd=1, relief="solid")
        ent_horario.pack(fill="x", pady=(2, 15))

        if indice_edicao is not None:
            item_id = tabela.get_children()[indice_edicao]
            val_nome = tabela.item(item_id, "text").strip()
            val_horario = tabela.item(item_id, "values")[0]
            ent_nome.insert(0, val_nome)
            ent_horario.insert(0, val_horario)

        def salvar():
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
                inserir_item_tabela(nome, horario)
            else:
                ao_editar(indice_edicao, nome, horario)
                item_id = tabela.get_children()[indice_edicao]
                tabela.item(item_id, text=f"  {nome}", values=(horario,))

            modal.destroy()

        btn_modal = criar_botao_arredondado(modal, "Save", salvar, width=120, height=32)
        btn_modal.pack(pady=5)

    btn_add = criar_botao_arredondado(frame_topo_tabela, "+ Add Reminder", lambda: abrir_modal_formulario(), width=120, height=32)
    btn_add.pack(side="right")

    def duplo_clique(_e):
        sel = tabela.selection()
        if not sel:
            return
        idx = tabela.index(sel[0])
        abrir_modal_formulario(idx)

    tabela.bind("<Double-1>", duplo_clique)

    def remover_selecionado():
        sel = tabela.selection()
        if not sel:
            return
        idx = tabela.index(sel[0])
        ao_remover(idx)
        tabela.delete(sel[0])

    tabela.bind("<Delete>", lambda _e: remover_selecionado())

    root.imagens_referencia = imagens_referencia
    return root, tabela


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

    popup.protocol("WM_DELETE_WINDOW", lambda: (ao_confirmar(), popup.destroy()))

    # Frame Principal
    container = tk.Frame(popup, bg="#FAF6F0", padx=15, pady=15)
    container.pack(fill="both", expand=True)

    # Lado Esquerdo: Eevee Frontal (eevee2.png)
    img_eevee = carregar_icone("eevee2.png", (140, 140))
    if not img_eevee:
        img_eevee = carregar_icone("eevee1.png", (140, 140))

    if img_eevee:
        lbl_img = tk.Label(container, image=img_eevee, bg="#FAF6F0")
        lbl_img.image = img_eevee
        lbl_img.pack(side="left", padx=(5, 15), anchor="c")

    # Lado Direito: Título + Subtítulo + Botões Empilhados
    frame_direito = tk.Frame(container, bg="#FAF6F0")
    frame_direito.pack(side="left", fill="both", expand=True)

    # Título Principal
    tk.Label(
        frame_direito,
        text="Next Medication",
        font=("Segoe UI", 14, "bold"),
        bg="#FAF6F0",
        fg="#1A1C2E",
        anchor="w",
    ).pack(fill="x", pady=(0, 2))

    # Detalhe do Remédio (ex: "teste — 02:15")
    tk.Label(
        frame_direito,
        text=mensagem,
        font=("Segoe UI", 9),
        bg="#FAF6F0",
        fg=TEXT_MUTED,
        anchor="w",
    ).pack(fill="x", pady=(0, 10))

    # Ações
    def acao_tomei():
        ao_confirmar()
        popup.destroy()

    def acao_adiar():
        ao_confirmar()
        if ao_adiar:
            ao_adiar()
        popup.destroy()

    # Botão "Confirm" (empilhado)
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

    # Botão "Snooze 5 Minutes" (empilhado)
    if ao_adiar:
        btn_snooze = criar_botao_arredondado(
            frame_direito,
            text="Snooze 5 minutes",
            command=acao_adiar,
            bg_color="#F5EBE1",
            fg_color="#1A1C2E",
            width=180,
            height=36,
            radius=10,
        )
        btn_snooze.pack(anchor="w")