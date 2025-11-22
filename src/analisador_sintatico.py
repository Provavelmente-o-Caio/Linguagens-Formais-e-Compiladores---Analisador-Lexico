from typing import List, Set
from src.gramaticas import (
    Terminal,
    NaoTerminal,
    Producao,
    EPSILON,
    Gramatica,
    HandlerGramatica,
)


class AnalisadorSintatico:
    """Analisador sintático SLR (Simple LR).
    
    Implementa gerador de analisadores sintáticos do tipo SLR a partir de
    gramáticas livres de contexto. Constrói tabelas ACTION e GOTO para
    parsing bottom-up.
    
    Referência: Aho et al., Seção 4.7
    """
    
    def __init__(self):
        """Inicializa o analisador sintático com estruturas vazias.
        
        O analisador usa um objeto Gramatica para encapsular todos os
        componentes da gramática (produções, símbolos, etc.).
        """
        self.gramatica: Gramatica | None = None
        self._handler: HandlerGramatica | None = None

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
        # Variáveis locais para construir gramática
        producoes: List[Producao] = []
        nao_terminais: Set[NaoTerminal] = set()
        terminais: Set[Terminal] = set()
        simbolo_inicial: NaoTerminal | None = None
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
                nao_terminais.add(cabeca)
                
                # Definir símbolo inicial (primeira produção)
                if simbolo_inicial is None:
                    simbolo_inicial = cabeca
                
                # Parsear corpo da produção
                try:
                    corpo = self._parsear_corpo(corpo_str, terminais, nao_terminais)
                except ValueError as e:
                    raise ValueError(
                        f"Erro na produção {numero_producao}: [{cabeca_str} ::= {corpo_str}], {e}"
                    )
                
                # Criar e armazenar produção
                producao = Producao(cabeca, tuple(corpo), numero_producao)
                producoes.append(producao)
                numero_producao += 1
                
                print(f"Produção {producao.numero}: {producao}")
        
        print(f"\nTotal: {len(producoes)} produções carregadas")
        print(f"Símbolo inicial: {simbolo_inicial}")
        print(f"Não-terminais: {sorted([str(nt) for nt in nao_terminais])}")
        print(f"Terminais: {sorted([str(t) for t in terminais])}")
        
        # Criar objeto Gramatica
        self.gramatica = Gramatica(
            producoes,
            terminais,
            nao_terminais,
            simbolo_inicial,
        )
    
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
    
    def _parsear_corpo(
        self, 
        corpo_str: str,
        terminais: Set[Terminal],
        nao_terminais: Set[NaoTerminal],
    ) -> List[Terminal | NaoTerminal]:
        """Parseia o corpo de uma produção extraindo símbolos.
        
        Identifica terminais (sem < >) e não-terminais (com < >).
        Produção vazia (ε) retorna lista vazia.
        
        Args:
            corpo_str: String contendo o corpo da produção.
            terminais: Conjunto para adicionar terminais encontrados.
            nao_terminais: Conjunto para adicionar não-terminais encontrados.
            
        Returns:
            Lista de símbolos (Simbolo) representando o corpo.
        """
        corpo_str = corpo_str.strip()
        
        # Produção vazia (epsilon)
        if corpo_str == EPSILON:
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
                nao_terminais.add(simbolo)
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
                    terminais.add(simbolo)
                    simbolos.append(simbolo)
                i = fim
        
        if simbolos == []:
            raise ValueError(
                f"Use epsilon {EPSILON} para representar produção vazia"
            )

        return simbolos
    
    def _obter_handler(self) -> HandlerGramatica:
        """Obtém ou cria handler de gramática para cálculos.
        
        Returns:
            Handler de gramática inicializado.
            
        Raises:
            ValueError: Se a gramática não foi carregada.
        """
        if self.gramatica is None:
            raise ValueError("Gramática não foi carregada. Use ler_gramatica() primeiro.")
        
        if self._handler is None:
            self._handler = HandlerGramatica(self.gramatica)
        
        return self._handler

