"""
gui.py
Interface grafica (Tkinter) — Fase 4.
- Janela principal: gerenciar (adicionar/remover) os horarios de lembrete.
- Pop-up: exibido quando um lembrete dispara.
"""

import tkinter as tk
from datetime import datetime
from tkinter import messagebox, ttk
from typing import Callable, TypedDict


class Lembrete(TypedDict):
    nome: str
    horario: str


def criar_janela_principal(
    lembretes_iniciais: list[Lembrete],
    ao_adicionar: Callable[[str, str], None],
    ao_remover: Callable[[int], None],
) -> tuple[tk.Tk, ttk.Treeview]:
    """
    Cria a janela principal do app, com a lista de lembretes cadastrados
    e campos para adicionar novos horarios.
    """
    root = tk.Tk()
    root.title("Eevee Reminder")
    root.geometry("400x420")
    root.resizable(False, False)

    tk.Label(root, text="Eevee Reminder", font=("Segoe UI", 16, "bold")).pack(pady=(15, 5))
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

    # --- formulario de novo lembrete ---------------------------------
    frame_form = tk.Frame(root)
    frame_form.pack(pady=(0, 10), padx=15, fill="x")

    tk.Label(frame_form, text="Medicamento:").grid(row=0, column=0, sticky="w")
    entrada_nome = tk.Entry(frame_form, width=20)
    entrada_nome.grid(row=0, column=1, padx=5)

    tk.Label(frame_form, text="Horario (HH:MM):").grid(row=1, column=0, sticky="w", pady=(8, 0))
    entrada_horario = tk.Entry(frame_form, width=20)
    entrada_horario.grid(row=1, column=1, padx=5, pady=(8, 0))

    def clicar_adicionar() -> None:
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

        ao_adicionar(nome, horario)
        tabela.insert("", "end", values=(nome, horario))
        entrada_nome.delete(0, "end")
        entrada_horario.delete(0, "end")

    tk.Button(frame_form, text="Adicionar", command=clicar_adicionar).grid(
        row=0, column=2, rowspan=2, padx=(10, 0)
    )

    # --- remover lembrete selecionado --------------------------------
    def clicar_remover() -> None:
        selecionado = tabela.selection()
        if not selecionado:
            messagebox.showinfo("Nada selecionado", "Selecione um lembrete na lista para remover.")
            return

        indice = tabela.index(selecionado[0])
        ao_remover(indice)
        tabela.delete(selecionado[0])

    tk.Button(root, text="Remover selecionado", command=clicar_remover).pack(pady=(0, 10))

    tk.Label(
        root,
        text="O app continua monitorando em segundo plano.\nFeche esta janela para encerrar o app.",
        font=("Segoe UI", 9),
        fg="gray",
    ).pack(pady=(10, 0))

    return root, tabela


def mostrar_popup(root: tk.Tk, mensagem: str, ao_confirmar: Callable[[], None]) -> None:
    popup = tk.Toplevel(root)
    popup.title("Lembrete de Medicamento")
    popup.geometry("320x160")
    popup.resizable(False, False)
    popup.attributes("-topmost", True)

    # impede fechar pelo "X" da janela — so o botao de confirmacao
    # pode fechar o pop-up e parar o som
    popup.protocol("WM_DELETE_WINDOW", lambda: None)

    tk.Label(popup, text="Hora do remedio!", font=("Segoe UI", 14, "bold")).pack(pady=(20, 10))
    tk.Label(popup, text=mensagem, font=("Segoe UI", 11)).pack(pady=(0, 20))

    def confirmar() -> None:
        ao_confirmar()
        popup.destroy()

    tk.Button(
        popup,
        text="Tomei o remedio ✓",
        font=("Segoe UI", 10, "bold"),
        command=confirmar,
    ).pack()