"""
config.py
Leitura e escrita dos horarios de lembrete em um arquivo JSON externo.
Fase 9: o arquivo de configuracao fica sempre ao lado do executavel (ou do
script), independente de estar rodando como .py ou empacotado como .exe.
"""

from __future__ import annotations

import json
from typing import TypedDict

from resources import pasta_dados


class Lembrete(TypedDict):
    nome: str
    horario: str  # formato "HH:MM"


PASTA_CONFIG = pasta_dados() / "config"
CAMINHO_CONFIG = PASTA_CONFIG / "reminders.json"

LEMBRETES_PADRAO: list[Lembrete] = [
    {"nome": "Vitamina C", "horario": "08:00"},
]


def carregar_lembretes() -> list[Lembrete]:
    """
    Carrega a lista de lembretes do arquivo de configuracao.
    Se o arquivo (ou a pasta) nao existir, cria com um lembrete padrao.
    """
    PASTA_CONFIG.mkdir(parents=True, exist_ok=True)

    if not CAMINHO_CONFIG.exists():
        salvar_lembretes(LEMBRETES_PADRAO)
        return list(LEMBRETES_PADRAO)

    try:
        with open(CAMINHO_CONFIG, "r", encoding="utf-8") as arquivo:
            dados = json.load(arquivo)
            return dados if isinstance(dados, list) else []
    except (json.JSONDecodeError, OSError) as erro:
        print(f"[aviso] erro ao ler {CAMINHO_CONFIG}: {erro}")
        return []


def salvar_lembretes(lembretes: list[Lembrete]) -> None:
    """Salva a lista de lembretes no arquivo de configuracao (formatado)."""
    PASTA_CONFIG.mkdir(parents=True, exist_ok=True)
    with open(CAMINHO_CONFIG, "w", encoding="utf-8") as arquivo:
        json.dump(lembretes, arquivo, ensure_ascii=False, indent=2)