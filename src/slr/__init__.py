"""Módulo de análise sintática SLR.

Referência: Dragon Book, Seção 4.7 "Analisadores Sintáticos LR".
"""

from .acoes import Shift, Reduce, Accept, Acao, ConflitoError
from .item_lr import ItemLR
from .tabela_slr import TabelaSLR
from .analisador_slr import AnalisadorSLR

__all__ = [
    'Shift',
    'Reduce',
    'Accept',
    'Acao',
    'ConflitoError',
    'ItemLR',
    'TabelaSLR',
    'AnalisadorSLR',
]
