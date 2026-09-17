"""
startup.py
Integracao com a inicializacao do Windows — Fase 8.
Usa a chave "Run" do Registro do Windows para iniciar o app
automaticamente junto com o sistema (sem precisar de instalador).
"""

import sys
import winreg
from pathlib import Path

NOME_APP = "EeveeReminder"
CHAVE_REGISTRO = r"Software\Microsoft\Windows\CurrentVersion\Run"


def _comando_execucao() -> str:
    """
    Monta o comando que o Windows vai rodar ao iniciar.
    - Se o app ja foi empacotado como .exe (pyinstaller), usa o proprio executavel.
    - Se ainda esta rodando como script .py, usa "python.exe" + caminho do main.py.
    """
    if getattr(sys, "frozen", False):
        return f'"{sys.executable}"'

    python_exe = sys.executable
    main_py = Path(__file__).resolve().parent / "main.py"
    return f'"{python_exe}" "{main_py}"'


def esta_habilitado() -> bool:
    """Verifica se o app ja esta registrado para iniciar com o Windows."""
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, CHAVE_REGISTRO, 0, winreg.KEY_READ) as chave:
            winreg.QueryValueEx(chave, NOME_APP)
            return True
    except FileNotFoundError:
        return False


def habilitar() -> None:
    """Adiciona o app a chave Run do Registro (passa a iniciar com o Windows)."""
    comando = _comando_execucao()
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, CHAVE_REGISTRO, 0, winreg.KEY_SET_VALUE) as chave:
        winreg.SetValueEx(chave, NOME_APP, 0, winreg.REG_SZ, comando)


def desabilitar() -> None:
    """Remove o app da chave Run do Registro."""
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, CHAVE_REGISTRO, 0, winreg.KEY_SET_VALUE) as chave:
            winreg.DeleteValue(chave, NOME_APP)
    except FileNotFoundError:
        pass  # ja estava desabilitado, nada a fazer