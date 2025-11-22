"""Conversor SLR para geração de parsers SLR(1).

Implementa a construção de itens LR(0) canônicos e tabelas de parsing SLR.

Referência: Aho et al., Seção 4.6 "Introduction to LR Parsing: Simple LR".
"""

from dataclasses import dataclass
from typing import Set, Dict, List, FrozenSet, Tuple
from src.gramaticas import (
    Gramatica,
    HandlerGramatica,
    Terminal,
    NaoTerminal,
    Producao,
    Epsilon,
)


@dataclass(frozen=True)
class ItemLR:
    """Representa um item LR(0): A ::= α·β
    
    Um item LR(0) indica uma posição de parsing dentro de uma produção.
    O ponto (·) marca até onde foi reconhecido.
    
    Referência: Aho et al., Seção 4.7
    
    Attributes:
        producao: Produção da gramática (A ::= αβ)
        posicao: Posição do ponto na produção (|α|)
    """
    producao: Producao
    posicao: int
    
    def __str__(self) -> str:
        """Representação em string: A ::= α·β"""
        corpo = self.producao.corpo
        prev = " ".join(str(s) for s in corpo[:self.posicao])
        post = " ".join(str(s) for s in corpo[self.posicao:])

        if prev and post:
            return f"{self.producao.cabeca} ::= {prev} · {post}"
        elif prev:
            return f"{self.producao.cabeca} ::= {prev} ·"
        elif post:
            return f"{self.producao.cabeca} ::= · {post}"
        else:
            return f"{self.producao.cabeca} ::= ·"
    
    def simbolo_apos_ponto(self) -> Terminal | NaoTerminal | None:
        """Retorna o símbolo imediatamente após o ponto, ou None se no final."""
        if self.posicao < len(self.producao.corpo):
            return self.producao.corpo[self.posicao]
        return None

    def esta_completo(self) -> bool:
        """Verifica se o item está completo (ponto no final)."""
        return self.posicao >= len(self.producao.corpo)
    
    def avancar(self) -> 'ItemLR':
        """Retorna novo item com ponto avançado uma posição."""
        return ItemLR(self.producao, self.posicao + 1)


class AnalisadorSLR:
    """Analisador SLR(1).
    
    Constrói a coleção canônica de conjuntos de itens LR(0) e
    gera tabelas ACTION e GOTO para parsing SLR.

    Referência: Aho et al., Seção 4.7
    """
    
    def __init__(self, gramatica: Gramatica, handler: HandlerGramatica):
        """Inicializa conversor com gramática e handler.
        
        Args:
            gramatica: Gramática livre do contexto
            handler: Handler para cálculos de FIRST e FOLLOW
        """
        self.gramatica = gramatica
        self.handler = handler
        
        # Gramática aumentada: S' ::= S
        self.estender_gramatica()
        
        # Coleção canônica de conjuntos de itens
        self.colecao_canonica: List[FrozenSet[ItemLR]] = []
        self.transicoes: Dict[Tuple[int, Terminal | NaoTerminal], int] = {}
        # Mapa para preservar ordem de inserção dos itens (para impressão)
        self.ordem_itens: Dict[FrozenSet[ItemLR], List[ItemLR]] = {}
    
    def estender_gramatica(self):
        self.simbolo_inicial_aumentado = NaoTerminal(f"{self.gramatica.simbolo_inicial.nome}'")
        self.producao_inicial = Producao(
            self.simbolo_inicial_aumentado,
            (self.gramatica.simbolo_inicial,),
            0
        )
        # Renumerar produções da gramática original (criar novas instâncias pois Producao é frozen)
        producoes_renumeradas = [
            Producao(p.cabeca, p.corpo, p.numero + 1) for p in self.gramatica.producoes
        ]
        self.gramatica.producoes = producoes_renumeradas

    def calcular_closure(self, itens: Set[ItemLR]) -> FrozenSet[ItemLR]:
        """Calcula o fechamento (closure) de um conjunto de itens LR(0).

        1. Inicialmente, adicione todos os itens de I a closure(I)
        2. Se A ::= α·Bβ está em closure(I) e B ::= γ ∈ P,
           adicione B ::= ·γ a closure(I) se ainda não estiver presente
        3. Repita até não haver mais itens a adicionar
        
        Preserva a ordem de inserção dos itens conforme Dragon Book.
        
        Args:
            itens: Conjunto inicial de itens
            
        Returns:
            Conjunto fechado de itens (frozen para usar como chave de dict)
        """
        # Lista ordenada para preservar ordem de inserção
        fechamento_ordenado = list(itens)
        # Set para verificação rápida de pertinência
        fechamento_set = set(itens)
        
        # Índice para processar itens (simula fila)
        i = 0
        while i < len(fechamento_ordenado):
            item = fechamento_ordenado[i]
            simbolo = item.simbolo_apos_ponto()
            
            # Se o símbolo após o ponto é não-terminal
            if isinstance(simbolo, NaoTerminal):
                # Adicionar todos os itens B ::= ·γ para cada B ::= γ
                for prod in self.gramatica.obter_producoes(simbolo):
                    novo_item = ItemLR(prod, 0)
                    if novo_item not in fechamento_set:
                        fechamento_ordenado.append(novo_item)
                        fechamento_set.add(novo_item)
            
            i += 1
        
        resultado = frozenset(fechamento_ordenado)
        # Armazenar ordem para impressão
        self.ordem_itens[resultado] = fechamento_ordenado
        return resultado
    
    def calcular_goto(self, itens: FrozenSet[ItemLR], simbolo: Terminal | NaoTerminal) -> FrozenSet[ItemLR]:
        """Calcula a função GOTO(I, X).

        GOTO(I, X) = closure({A ::= αX·β | A ::= α·Xβ ∈ I})
        
        Preserva a ordem dos itens conforme aparecem no conjunto original.
        
        Args:
            itens: Conjunto de itens
            simbolo: Símbolo da gramática
            
        Returns:
            Conjunto de itens após transição por símbolo
        """
        # Usar ordem preservada do conjunto de itens
        itens_ordenados = self.ordem_itens.get(itens, list(itens))
        conjunto_j = []
        
        for item in itens_ordenados:
            # Se o item tem X após o ponto
            if item.simbolo_apos_ponto() == simbolo:
                # Adicionar item com ponto avançado
                conjunto_j.append(item.avancar())
        
        if not conjunto_j:
            return frozenset()
        
        return self.calcular_closure(set(conjunto_j))
    
    def construir_colecao_canonica(self) -> List[FrozenSet[ItemLR]]:
        """Constrói a coleção canônica de conjuntos de itens LR(0).

        1. C = {closure({S' ::= ·S})}
        2. Para cada I ∈ C e cada símbolo X:
           - Se goto(I, X) não vazio e não em C, adicione a C
        3. Repita até não haver mais conjuntos a adicionar
        
        Returns:
            Lista de conjuntos de itens (estados do autômato LR)
        """
        # Estado inicial I0 = closure({S' ::= ·S})
        item_inicial = ItemLR(self.producao_inicial, 0)
        estado_inicial = self.calcular_closure({item_inicial})
        
        self.colecao_canonica = [estado_inicial]
        self.transicoes = {}
        
        # Mapa de conjunto -> índice para busca rápida
        indice_conjuntos: Dict[FrozenSet[ItemLR], int] = {estado_inicial: 0}
        
        # Fila de estados a processar
        q = [0]
        
        while q:
            idx = q.pop(0)
            conjunto_atual = self.colecao_canonica[idx]
            
            # Coletar todos os símbolos que aparecem após o ponto (preservando ordem)
            simbolos_ordenados = []
            simbolos_vistos = set()
            itens_ordenados = self.ordem_itens.get(conjunto_atual, list(conjunto_atual))
            
            for item in itens_ordenados:
                simbolo = item.simbolo_apos_ponto()
                if simbolo is not None and simbolo not in simbolos_vistos:
                    simbolos_ordenados.append(simbolo)
                    simbolos_vistos.add(simbolo)
            
            # Para cada símbolo, calcular goto
            for simbolo in simbolos_ordenados:
                goto_conjunto = self.calcular_goto(conjunto_atual, simbolo)
                
                if not goto_conjunto:
                    continue
                
                # Verificar se já existe na coleção
                if goto_conjunto not in indice_conjuntos:
                    # Novo estado
                    prox_idx = len(self.colecao_canonica)
                    self.colecao_canonica.append(goto_conjunto)
                    indice_conjuntos[goto_conjunto] = prox_idx
                    q.append(prox_idx)
                    idx_destino = prox_idx
                else:
                    idx_destino = indice_conjuntos[goto_conjunto]
                
                # Armazenar transição
                self.transicoes[f"{idx},{simbolo}"] = idx_destino
        
        return self.colecao_canonica
    
    def imprimir_colecao_canonica(self):
        """Imprime a coleção canônica de forma legível."""
        if not self.colecao_canonica:
            self.construir_colecao_canonica()
        
        print("\n=== COLEÇÃO CANÔNICA DE ITENS LR(0) ===\n")
        
        for i, conjunto in enumerate(self.colecao_canonica):
            print(f"Estado I{i}:")
            # Usar ordem de inserção preservada durante closure
            itens_ordenados = self.ordem_itens.get(conjunto, list(conjunto))
            for item in itens_ordenados:
                print(f"  {item}")
            print()
        
        print("\n=== TRANSIÇÕES ===\n")
        # Ordenar transições por número de estado de origem
        transicoes_ordenadas = sorted(
            self.transicoes.items(),
            key=lambda x: int(x[0].split(",")[0])
        )
        for origem, destino in transicoes_ordenadas:
            estado, simbolo = origem.split(",", 1)
            print(f"I{estado} --{simbolo}--> I{destino}")
