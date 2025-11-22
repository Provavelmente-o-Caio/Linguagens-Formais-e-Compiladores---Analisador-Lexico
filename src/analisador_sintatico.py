"""Analisador sintático SLR.

Implementa gerador de analisadores sintáticos do tipo SLR (Simple LR)
a partir de gramáticas livres de contexto.

Referência: Aho et al., Seção 4.6 "Introduction to LR Parsing: Simple LR".
"""

from typing import List, Set
from src.gramaticas import (
    Terminal,
    NaoTerminal,
    Producao,
    Epsilon,
)


class AnalisadorSintatico:
    """Analisador sintático SLR (Simple LR).
    
    Implementa gerador de analisadores sintáticos do tipo SLR a partir de
    gramáticas livres de contexto. Constrói tabelas ACTION e GOTO para
    parsing bottom-up.
    
    Referência: Aho et al., Seção 4.6 "Introduction to LR Parsing: Simple LR".
    """
    
    def __init__(self):
        """Inicializa o analisador sintático com estruturas vazias.
        
        Inicializa gramática, conjunto de símbolos, produções e estruturas
        para construção das tabelas de parsing.
        """
        self.producoes: List[Producao] = []
        self.nao_terminais: Set[NaoTerminal] = set()
        self.terminais: Set[Terminal] = set()
        self.simbolo_inicial: NaoTerminal | None = None

    def ler_gramatica(self, arquivo: str):
        """Lê gramática livre de contexto de um arquivo.
        
        Formato esperado: <Não terminal> ::= <Corpo da produção>
        Linhas começando com # são tratadas como comentários.
        Linhas vazias são ignoradas.
        
        A primeira produção define o símbolo inicial da gramática.
        
        Args:
            arquivo: Caminho do arquivo contendo a gramática.
            
        Raises:
            ValueError: Se encontrar linha com formato inválido.
        """
        numero_producao = 0
        
        with open(arquivo, "r") as f:
            for num_linha, linha in enumerate(f, 1):
                linha = linha.strip()
                
                # Ignorar comentários e linhas vazias
                if linha.startswith("#") or not linha:
                    continue
                
                # Verificar formato básico
                if "::=" not in linha:
                    raise ValueError(
                        f"Linha {num_linha} com formato inválido. "
                        f"Esperava '<Não terminal> ::= <Corpo>', obteve: {linha}"
                    )
                
                # Separar cabeça e corpo
                partes = linha.split("::=")
                if len(partes) != 2:
                    raise ValueError(
                        f"Linha {num_linha} com formato inválido. "
                        f"Esperava exatamente um '::=', obteve: {linha}"
                    )
                
                cabeca_str = partes[0].strip()
                corpo_str = partes[1].strip()
                
                # Remover delimitadores < > da cabeça
                cabeca_str = self._limpar_simbolo(cabeca_str)
                
                if not cabeca_str:
                    raise ValueError(
                        f"Linha {num_linha} com não-terminal vazio. "
                        f"Obteve: {linha}"
                    )
                
                # Criar símbolo não-terminal da cabeça
                cabeca = NaoTerminal(cabeca_str)
                self.nao_terminais.add(cabeca)
                
                # Definir símbolo inicial (primeira produção)
                if self.simbolo_inicial is None:
                    self.simbolo_inicial = cabeca
                
                # Parsear corpo da produção
                try:
                    corpo = self._parsear_corpo(corpo_str)
                except ValueError as e:
                    raise ValueError(
                        f"Erro na produção {numero_producao}: [{cabeca_str} ::= {corpo_str}], {e}"
                    )
                
                # Criar e armazenar produção
                producao = Producao(cabeca, corpo, numero_producao)
                self.producoes.append(producao)
                numero_producao += 1
                
                print(f"Produção {producao.numero}: {producao}")
        
        print(f"\nTotal: {len(self.producoes)} produções carregadas")
        print(f"Símbolo inicial: {self.simbolo_inicial}")
        print(f"Não-terminais: {sorted([str(nt) for nt in self.nao_terminais])}")
        print(f"Terminais: {sorted([str(t) for t in self.terminais])}")
    
    def _limpar_simbolo(self, simbolo_str: str) -> str:
        """Remove delimitadores < > de um símbolo.
        
        Args:
            simbolo_str: String contendo o símbolo, possivelmente com < >.
            
        Returns:
            String limpa sem os delimitadores.
        """
        simbolo_str = simbolo_str.strip()
        if simbolo_str.startswith("<") and simbolo_str.endswith(">"):
            simbolo_str = simbolo_str[1:-1].strip()
        return simbolo_str
    
    def _parsear_corpo(self, corpo_str: str) -> List[Terminal | NaoTerminal]:
        """Parseia o corpo de uma produção extraindo símbolos.
        
        Identifica terminais (sem < >) e não-terminais (com < >).
        Produção vazia (ε) retorna lista vazia.
        
        Args:
            corpo_str: String contendo o corpo da produção.
            
        Returns:
            Lista de símbolos (Simbolo) representando o corpo.
        """
        corpo_str = corpo_str.strip()
        
        # Produção vazia (epsilon)
        if corpo_str == Epsilon():
            return []

        simbolos = []
        i = 0
        
        while i < len(corpo_str):
            # Pular espaços
            if corpo_str[i].isspace():
                i += 1
                continue
            
            # Não-terminal: <...>
            if corpo_str[i] == "<":
                fim = corpo_str.find(">", i)
                if fim == -1:
                    raise ValueError(
                        f"Não-terminal não fechado: {corpo_str[i:]}"
                    )
                nome = corpo_str[i+1:fim].strip()
                simbolo = NaoTerminal(nome)
                self.nao_terminais.add(simbolo)
                simbolos.append(simbolo)
                i = fim + 1
            else:
                # Terminal: qualquer outro caractere ou sequência
                # Ler até próximo < ou espaço
                fim = i + 1
                while fim < len(corpo_str) and corpo_str[fim] not in ["<", " "]:
                    fim += 1
                
                nome = corpo_str[i:fim].strip()
                if nome:  # Evitar strings vazias
                    simbolo = Terminal(nome)
                    self.terminais.add(simbolo)
                    simbolos.append(simbolo)
                i = fim
        
        if simbolos == []:
            raise ValueError(
                f"Use epsilon {Epsilon()} para representar produção vazia"
            )

        return simbolos
