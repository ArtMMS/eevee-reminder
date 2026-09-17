"""
resources.py
Resolve caminhos de arquivos, funcionando tanto rodando como script (.py)
quanto empacotado como executavel (.exe) pelo PyInstaller — Fase 9.
"""

import sys
from pathlib import Path


def pasta_recursos() -> Path:
    """
    Pasta dos recursos 'somente leitura' empacotados no .exe (sons, icones).
    Quando rodando como .exe, o PyInstaller extrai esses arquivos para uma
    pasta temporaria, acessivel via sys._MEIPASS.
    """
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS)  # type: ignore[attr-defined]
    return Path(__file__).resolve().parent


def pasta_dados() -> Path:
    """
    Pasta dos dados que o usuario pode alterar (config/reminders.json).
    Precisa ficar ao LADO do .exe (nao dentro do pacote temporario), para
    que as alteracoes sejam salvas de verdade entre execucoes.
    """
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent