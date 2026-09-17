"""
gui.py
Interface grafica (Tkinter) — Fase 8.
- Janela principal: gerenciar (adicionar, editar, remover) horarios + botao de configuracoes.
- Janela de configuracoes: liga/desliga o inicio automatico com o Windows.
- Pop-up: exibido quando um lembrete dispara, contendo as opcoes de confirmar e adiar.
"""

import tkinter as tk
from datetime import datetime
from tkinter import messagebox, ttk
from typing import Callable, Optional, TypedDict


class Lembrete(TypedDict):
    nome: str
    horario: str


def criar_janela_principal(
    lembretes_iniciais: list[Lembrete],
    ao_adicionar: Callable[[str, str], None],
    ao_editar: Callable[[int, str, str], None],
    ao_remover: Callable[[int], None],
    obter_iniciar_com_windows: Callable[[], bool],
    ao_alternar_iniciar_com_windows: Callable[[bool], None],
) -> tuple[tk.Tk, ttk.Treeview]:
    """
    Cria a janela principal do app: lista de lembretes, formulario de
    adicionar/editar, botao de remover e botao de configuracoes (⚙).
    """
    root = tk.Tk()
    root.title("Eevee Reminder")
    root.geometry("400x480")
    root.resizable(False, False)

    indice_em_edicao: Optional[int] = None

    # --- barra superior com o botao de configuracoes ------------------
    frame_topo = tk.Frame(root)
    frame_topo.pack(fill="x")

    tk.Button(
        frame_topo,
        text="⚙",
        font=("Segoe UI", 11),
        width=3,
        command=lambda: abrir_janela_configuracoes(
            root, obter_iniciar_com_windows, ao_alternar_iniciar_com_windows
        ),
    ).pack(side="right", padx=10, pady=8)

    tk.Label(root, text="Eevee Reminder", font=("Segoe UI", 16, "bold")).pack(pady=(0, 5))
    tk.Label(root, text="Seus lembretes de medicamento", font=("Segoe UI", 10)).pack()

    # --- tabela de lembretes cadastrados -----------------------------
    tabela = ttk.Treeview(root, columns=("nome", "horario"), show="headings", height=8)
    tabela.heading("nome", text="Medicamento")
    tabela.heading("horario", text="Horario")
    tabela.column("nome", width=220)
    tabela.column("horario", width=100, anchor="center")
    tabela.pack(pady=15, padx=15, fill="x")

    for lembrete in lembretes_iniciais:
        tabela.insert("", "end", values=(lembrete["nome"], lembrete["horario"]))

    tk.Label(
        root, text="Dica: dê dois cliques para editar ou pressione DEL para remover",
        font=("Segoe UI", 8), fg="gray",
    ).pack()

    # --- formulario de adicionar/editar -------------------------------
    frame_form = tk.Frame(root)
    frame_form.pack(pady=(10, 5), padx=15, fill="x")

    tk.Label(frame_form, text="Medicamento:").grid(row=0, column=0, sticky="w")
    entrada_nome = tk.Entry(frame_form, width=20)
    entrada_nome.grid(row=0, column=1, padx=5)

    tk.Label(frame_form, text="Horario (HH:MM):").grid(row=1, column=0, sticky="w", pady=(8, 0))
    entrada_horario = tk.Entry(frame_form, width=20)
    entrada_horario.grid(row=1, column=1, padx=5, pady=(8, 0))

    botao_confirmar = tk.Button(frame_form, text="Adicionar")
    botao_confirmar.grid(row=0, column=2, rowspan=2, padx=(10, 0))

    def limpar_formulario() -> None:
        nonlocal indice_em_edicao
        indice_em_edicao = None
        entrada_nome.delete(0, "end")
        entrada_horario.delete(0, "end")
        botao_confirmar.config(text="Adicionar")

    def clicar_confirmar() -> None:
        nonlocal indice_em_edicao
        nome = entrada_nome.get().strip()
        horario = entrada_horario.get().strip()

        if not nome:
            messagebox.showwarning("Campo vazio", "Digite o nome do medicamento.")
            return

        try:
            datetime.strptime(horario, "%H:%M")
        except ValueError:
            messagebox.showwarning("Horario invalido", "Use o formato HH:MM (ex: 08:30).")
            return

        if indice_em_edicao is None:
            ao_adicionar(nome, horario)
            tabela.insert("", "end", values=(nome, horario))
        else:
            ao_editar(indice_em_edicao, nome, horario)
            item_id = tabela.get_children()[indice_em_edicao]
            tabela.item(item_id, values=(nome, horario))

        limpar_formulario()

    botao_confirmar.config(command=clicar_confirmar)

    def clicar_duplo(_evento) -> None:
        nonlocal indice_em_edicao
        selecionado = tabela.selection()
        if not selecionado:
            return

        indice_em_edicao = tabela.index(selecionado[0])
        nome_atual, horario_atual = tabela.item(selecionado[0], "values")

        entrada_nome.delete(0, "end")
        entrada_nome.insert(0, nome_atual)
        entrada_horario.delete(0, "end")
        entrada_horario.insert(0, horario_atual)
        botao_confirmar.config(text="Salvar edicao")

    tabela.bind("<Double-1>", clicar_duplo)

    def clicar_remover() -> None:
        selecionado = tabela.selection()
        if not selecionado:
            messagebox.showinfo("Nada selecionado", "Selecione um lembrete na lista para remover.")
            return

        indice = tabela.index(selecionado[0])
        ao_remover(indice)
        tabela.delete(selecionado[0])
        limpar_formulario()

    # Atalho para remover ao pressionar a tecla Delete (DEL) na tabela
    tabela.bind("<Delete>", lambda _evento: clicar_remover())

    frame_botoes = tk.Frame(root)
    frame_botoes.pack(pady=(5, 10))
    tk.Button(frame_botoes, text="Remover selecionado", command=clicar_remover).grid(row=0, column=0, padx=5)
    tk.Button(frame_botoes, text="Cancelar edicao", command=limpar_formulario).grid(row=0, column=1, padx=5)

    tk.Label(
        root,
        text="O app continua monitorando em segundo plano.\nFeche esta janela para encerrar o app.",
        font=("Segoe UI", 9),
        fg="gray",
    ).pack(pady=(10, 0))

    return root, tabela


def abrir_janela_configuracoes(
    root: tk.Tk,
    obter_iniciar_com_windows: Callable[[], bool],
    ao_alternar_iniciar_com_windows: Callable[[bool], None],
) -> None:
    """
    Abre a janela de configuracoes. Por enquanto tem apenas a opcao
    de iniciar automaticamente junto com o Windows.
    """
    janela = tk.Toplevel(root)
    janela.title("Configurações")
    janela.geometry("320x160")
    janela.resizable(False, False)
    janela.attributes("-topmost", True)

    tk.Label(janela, text="Configurações", font=("Segoe UI", 13, "bold")).pack(pady=(20, 15))

    valor_atual = obter_iniciar_com_windows()
    variavel_iniciar = tk.BooleanVar(value=valor_atual)

    def clicar_toggle() -> None:
        ao_alternar_iniciar_com_windows(variavel_iniciar.get())

    tk.Checkbutton(
        janela,
        text="Iniciar automaticamente com o Windows",
        variable=variavel_iniciar,
        font=("Segoe UI", 10),
        command=clicar_toggle,
    ).pack(padx=20, anchor="w")

    tk.Button(janela, text="Fechar", command=janela.destroy).pack(pady=(20, 0))


def mostrar_popup(
    root: tk.Tk, 
    mensagem: str, 
    ao_confirmar: Callable[[], None],
    ao_adiar: Optional[Callable[[], None]] = None
) -> None:
    """
    Exibe um alerta contendo as opções de confirmar o remédio tomado 
    ou adiar o lembrete por alguns minutos (Snooze).
    """
    popup = tk.Toplevel(root)
    popup.title("Lembrete de Medicamento")
    popup.geometry("340x180")
    popup.resizable(False, False)
    popup.attributes("-topmost", True)
    
    def acao_fechar_x() -> None:
        ao_confirmar()
        popup.destroy()

    popup.protocol("WM_DELETE_WINDOW", acao_fechar_x)

    tk.Label(popup, text="Hora do remédio!", font=("Segoe UI", 14, "bold")).pack(pady=(15, 5))
    tk.Label(popup, text=mensagem, font=("Segoe UI", 11)).pack(pady=(0, 15))

    frame_acoes = tk.Frame(popup)
    frame_acoes.pack(pady=5)

    def confirmar() -> None:
        ao_confirmar()
        popup.destroy()

    def adiar() -> None:
        ao_confirmar()  # Para o som do alarme
        if ao_adiar:
            ao_adiar()  # Reagenda o lembrete para +5 minutos
        popup.destroy()

    tk.Button(
        frame_acoes,
        text="Tomei ✓",
        font=("Segoe UI", 10, "bold"),
        command=confirmar,
        width=12,
    ).grid(row=0, column=0, padx=5)

    if ao_adiar:
        tk.Button(
            frame_acoes,
            text="Adiar 5 min ⏱",
            font=("Segoe UI", 10),
            command=adiar,
            width=12,
        ).grid(row=0, column=1, padx=5)