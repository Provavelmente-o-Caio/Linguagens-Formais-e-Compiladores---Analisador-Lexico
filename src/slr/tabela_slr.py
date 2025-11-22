from typing import Dict, List, FrozenSet, Tuple
from src.gramaticas import Terminal, NaoTerminal, Producao, HandlerGramatica
from .acoes import Acao, Shift, Reduce, Accept, ConflitoError
from .item_lr import ItemLR


class TabelaSLR:
    """Tabela de parsing SLR contendo ACTION e GOTO.
    
    Referência: Aho et al., Seção 4.7
    """
    
    def __init__(self):
        """Inicializa tabelas vazias."""
        # ACTION[estado, terminal] -> ação (Shift, Reduce ou Accept)
        self.action: Dict[Tuple[int, Terminal], Acao] = {}
        # GOTO[estado, não-terminal] -> estado
        self.goto: Dict[Tuple[int, NaoTerminal], int] = {}
        # Lista de conflitos encontrados
        self.conflitos: List[ConflitoError] = []

    def construir(
        self,
        colecao_canonica: List[FrozenSet[ItemLR]],
        ordem_itens: Dict[FrozenSet[ItemLR], List[ItemLR]],
        transicoes: Dict[str, int],
        producao_inicial: Producao,
        handler: HandlerGramatica
    ):
        """Constrói as tabelas ACTION e GOTO para o parser SLR.
        
        Algoritmo de construção da tabela SLR
        Para cada estado I_i:
        1. Se [A ::= α·aβ] ∈ I_i e goto(I_i, a) = I_j, então ACTION[i,a] = shift j
        2. Se [A ::= α·] ∈ I_i, então ACTION[i,a] = reduce A::=α para todo a ∈ FOLLOW(A)
           (A ≠ S')
        3. Se [S' ::= S·] ∈ I_i, então ACTION[i,$] = accept
        4. Se goto(I_i, A) = I_j, então GOTO[i,A] = j
        
        Args:
            colecao_canonica: Lista de conjuntos de itens LR(0)
            ordem_itens: Mapa preservando ordem de inserção dos itens
            transicoes: Dicionário de transições entre estados
            producao_inicial: Produção aumentada S' ::= S
            handler: Handler para cálculos de FOLLOW
        """
        # Terminal de fim de entrada
        fim_entrada = Terminal("$")
        
        for i, conjunto in enumerate(colecao_canonica):
            itens_ordenados = ordem_itens.get(conjunto, list(conjunto))
            
            for item in itens_ordenados:
                simbolo = item.simbolo_apos_ponto()
                
                # Regra 1: Se [A ::= α·aβ] e a é terminal
                if simbolo is not None and isinstance(simbolo, Terminal):
                    # Procurar transição goto(I_i, a)
                    chave_trans = (i, simbolo)
                    if chave_trans in transicoes:
                        j = transicoes[chave_trans]
                        nova_acao = Shift(j)
                        # Verificar conflito
                        acao_anterior = self.action.get((i, simbolo))
                        if acao_anterior and acao_anterior != nova_acao:
                            raise ConflitoError(i, simbolo, str(acao_anterior), str(nova_acao))
                        self.action[(i, simbolo)] = nova_acao
                
                # Regra 2 e 3: Se [A ::= α·] (item completo)
                elif item.esta_completo():
                    # Regra 3: Aceitar se for S' ::= S·
                    if item.producao == producao_inicial:
                        self.action[(i, fim_entrada)] = Accept()
                    # Regra 2: Reduce para FOLLOW(A)
                    else:
                        producao = item.producao
                        follow_a = handler.get_follow(producao.cabeca)
                        
                        for terminal in follow_a:
                            nova_acao = Reduce(producao.numero)
                            # Verificar conflito
                            acao_anterior = self.action.get((i, terminal))
                            if acao_anterior and acao_anterior != nova_acao:
                                raise ConflitoError(i, terminal, str(acao_anterior), str(nova_acao))
                            self.action[(i, terminal)] = nova_acao
            
            # Regra 4: Preencher GOTO para não-terminais
            itens_ordenados = ordem_itens.get(conjunto, list(conjunto))
            simbolos_goto = []
            for item in itens_ordenados:
                simbolo = item.simbolo_apos_ponto()
                if simbolo is not None and isinstance(simbolo, NaoTerminal):
                    if simbolo not in simbolos_goto:
                        simbolos_goto.append(simbolo)
            
            for nt in simbolos_goto:
                chave_trans = (i, nt)
                if chave_trans in transicoes:
                    j = transicoes[chave_trans]
                    self.goto[(i, nt)] = j
