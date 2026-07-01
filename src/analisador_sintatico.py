from typing import List, Set

from src.expressaoregular import MAPA_OPERADORES, OPERADORES_UNITARIOS
from src.gramaticas import (
    EPSILON,
    NAO_TERMINAL_ESCAPE,
    Gramatica,
    HandlerGramatica,
    NaoTerminal,
    Producao,
    Terminal,
)
from src.ll.analisador_ll1 import AnalisadorLL1
from src.ll.parser_ll1 import ParserLL1
from src.tabela_simbolos import CategoriaLexica, Escopo
from src.sdd import SDD


class AnalisadorSintatico:
    def __init__(self):
        """Inicializa o analisador sintático com estruturas vazias.

        O analisador usa um objeto Gramatica para encapsular todos os
        componentes da gramática (produções, símbolos, etc.).
        """
        self.gramatica: Gramatica | None = None
        self._handler: HandlerGramatica | None = None
        self.arquivo_tokens: str | None = None
        self.escopo_global: Escopo | None = None
        self.escopo_atual: Escopo | None = None
        self.tabela_simbolos = None
        self.codigo_intermediario: str = ""
        self.sdd: SDD | None = None
        self.tipo_prox_loop = None

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
                        f"Linha {num_linha} com não-terminal vazio. Obteve: {linha}"
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

            # Terminal escapado: "..."
            if corpo_str[i] == NAO_TERMINAL_ESCAPE:
                fim = corpo_str.find(NAO_TERMINAL_ESCAPE, i + 1)
                if fim == -1:
                    raise ValueError(f"Terminal escapado não fechado: {corpo_str[i:]}")
                nome = corpo_str[i + 1 : fim]
                simbolo = Terminal(nome)
                terminais.add(simbolo)
                simbolos.append(simbolo)
                i = fim + 1
            # Não-terminal: <...>
            elif corpo_str[i] == "<":
                fim = corpo_str.find(">", i)
                if fim == -1:
                    raise ValueError(f"Não-terminal não fechado: {corpo_str[i:]}")
                nome = corpo_str[i + 1 : fim].strip()
                simbolo = NaoTerminal(nome)
                nao_terminais.add(simbolo)
                simbolos.append(simbolo)
                i = fim + 1
            else:
                # Terminal: qualquer outro caractere ou sequência
                # Ler até próximo < ou espaço ou "
                fim = i + 1
                while fim < len(corpo_str) and corpo_str[fim] not in [
                    "<",
                    " ",
                    NAO_TERMINAL_ESCAPE,
                ]:
                    fim += 1

                nome = corpo_str[i:fim].strip()
                if nome:  # Evitar strings vazias
                    simbolo = Terminal(nome)
                    terminais.add(simbolo)
                    simbolos.append(simbolo)
                i = fim

        if simbolos == []:
            raise ValueError(f"Use epsilon {EPSILON} para representar produção vazia")

        return simbolos

    def _obter_handler(self) -> HandlerGramatica:
        """Obtém ou cria handler de gramática para cálculos.

        Returns:
            Handler de gramática inicializado.

        Raises:
            ValueError: Se a gramática não foi carregada.
        """
        if not self.gramatica:
            raise ValueError("Gramática não foi carregada ainda")

        if not self._handler:
            self._handler = HandlerGramatica(self.gramatica)

        return self._handler

    def _criar_tabela_simbolos(self):
        """Cria tabela de símbolos e extrai palavras reservadas da gramática.

        Returns:
            TabelaSimbolos inicializada com palavras reservadas
        """
        self.escopo_global = Escopo("0")
        self.escopo_atual = self.escopo_global
        self.tabela_simbolos = self.escopo_global.tabela

        palavras_reservadas = {
            "def",
            "if",
            "else",
            "for",
            "break",
            "return",
            "print",
            "read",
            "new",
            "int",
            "float",
            "string",
            "null",
        }

        for palavra in palavras_reservadas:
            self.escopo_global.tabela.inserir_palavra_reservada(palavra)



    def _processar_tokens(self, tokens: list[tuple[str, str]]) -> list[tuple[str, str]]:
        """Processa tokens aplicando tabela de símbolos e mapeamento para gramática.

        Args:
            tokens: Lista de tuplas (lexema, tipo)

        Returns:
            Lista de tokens processados e mapeados
        """
        # Construir mapa automático: lexema → terminal
        mapa_lexema_terminal = {}
        for terminal in self.gramatica.terminais:
            if len(terminal.nome) <= 2 and not terminal.nome.isalnum():
                mapa_lexema_terminal[terminal.nome] = terminal.nome

        tokens_processados = []
        for lexema, tipo_lexico in tokens:
            if tipo_lexico in CategoriaLexica.categorias_processaveis():
                _, categoria = self.escopo_atual.tabela.categorizar_token(
                    lexema, tipo_lexico
                )

                if CategoriaLexica.palavra_reservada(categoria):
                    tipo_gramatica = lexema
                elif categoria.isdigit():
                    tipo_gramatica = "id"
                else:
                    tipo_gramatica = tipo_lexico


                if lexema in {"for", "while"}:
                    self.tipo_prox_loop = lexema

                if lexema == "{":
                    self.escopo_atual = self.escopo_atual.aumentar_escopo(tipo=self.tipo_prox_loop)
                    self.tipo_prox_loop = None
                elif lexema == "}":
                    self.escopo_atual = (
                        self.escopo_atual.reduzir_escopo()
                        if self.escopo_atual.reduzir_escopo()
                        else self.escopo_atual
                    ) 
                    self.tipo_prox_loop = None

                if lexema == "break":
                    if self.escopo_atual.tipo not in {"for", "while"}:
                        raise ValueError(
                            f"Token 'break' fora de loop em escopo {self.escopo_atual.numero}"
                        )

                tokens_processados.append((lexema, tipo_gramatica))
            else:
                if lexema in mapa_lexema_terminal:
                    tokens_processados.append((lexema, lexema))
                else:
                    tokens_processados.append((lexema, tipo_lexico))

        return tokens_processados

    def _normalizar_lexema(self, lexema: str) -> str:
        """Normaliza lexema Unicode de volta para ASCII.

        Usa os mapas de operadores de expressaoregular.py para converter
        símbolos Unicode (⊕, ×, etc.) de volta para ASCII (+, *, etc.).

        Args:
            lexema: Lexema possivelmente em Unicode

        Returns:
            Lexema normalizado em ASCII
        """
        mapa_reverso = {}

        # MAPA_OPERADORES: multi-caractere (>=, <=, ==, etc.)
        for ascii_op, unicode_op in MAPA_OPERADORES.items():
            mapa_reverso[unicode_op] = ascii_op

        # OPERADORES_UNITARIOS: single-caractere (+, -, *, etc.)
        for ascii_op, unicode_op in OPERADORES_UNITARIOS.items():
            mapa_reverso[unicode_op] = ascii_op

        return mapa_reverso.get(lexema, lexema)

    def _ler_tokens_arquivo(self, arquivo: str) -> list[tuple[str, str]]:
        """Lê tokens de um arquivo no formato <lexema, tipo>.

        Args:
            arquivo: Caminho do arquivo de tokens

        Returns:
            Lista de tuplas (lexema, tipo)
        """
        tokens = []
        with open(arquivo, "r") as f:
            for linha in f:
                linha = linha.strip()
                if not linha or linha.startswith("#"):
                    continue

                # Formato esperado: <lexema, tipo>
                if linha.startswith("<") and linha.endswith(">"):
                    conteudo = linha[1:-1]  # Remove < e >
                    if ", " in conteudo:
                        partes = conteudo.split(", ", 1)
                        if len(partes) == 2:
                            lexema, tipo = partes
                            # Normalizar lexema para ASCII
                            lexema = self._normalizar_lexema(lexema)
                            tokens.append((lexema, tipo))

        print(f"Tokens carregados com successo do arquivo [{arquivo}]")

        return tokens

    def _aplicar_sdd(self, tokens_brutos: list[tuple[str, str]]):
        """Aplica as regras SDD após a aceitação sintática.

        Atualmente o SDD cobre a propagação de tipos em declarações,
        atualizando a tabela de símbolos com os atributos sintetizados.
        """

        if not self.escopo_global:
            return

        self.sdd = SDD(self.escopo_global)
        self.sdd.aplicar(tokens_brutos)

        self.tabela_simbolos = self.escopo_global.tabela

    def analisar_ll1(self, arquivo_tokens: str, completo: bool = False) -> bool:
        self._criar_tabela_simbolos()

        tokens_brutos = self._ler_tokens_arquivo(arquivo_tokens)
        tokens = self._processar_tokens(tokens_brutos)

        handler = self._obter_handler()
        handler.calcular_firsts()
        handler.calcular_follows()

        if not self.gramatica:
            return False

        analisador_ll1 = AnalisadorLL1(self.gramatica, handler)
        tabela = analisador_ll1.construir_tabela()

        parser = ParserLL1(tabela, self.gramatica)
        resultado = parser.parsear(tokens)

        if resultado:
            self._aplicar_sdd(tokens_brutos)

        if resultado and not completo:
            print("SENTENÇA ACEITA!")
            parser.imprimir_derivacao()
        elif not resultado:
            print("ERRO SINTÁTICO!")

        if completo:
            return resultado, handler, analisador_ll1, parser

        return resultado

    """
    def analisar_ll1(self, arquivo_tokens: str, completo: bool = False) -> bool:
        self._criar_tabela_simbolos()

        tokens_brutos = self._ler_tokens_arquivo(arquivo_tokens)
        tokens = self._processar_tokens(tokens_brutos)

        handler = self._obter_handler()
        handler.calcular_firsts()
        handler.calcular_follows()

        if self.gramatica:
            analisador_ll1 = AnalisadorLL1(self.gramatica, handler)
            tabela = analisador_ll1.construir_tabela()

            parser = ParserLL1(tabela, self.gramatica)
            resultado = parser.parsear(tokens)

            if resultado:
                self._aplicar_sdd(tokens_brutos)

            if resultado and not completo:
                print("SENTENÇA ACEITA!")
                parser.imprimir_derivacao()
            elif not resultado:
                print("ERRO SINTÁTICO!")
        self._criar_tabela_simbolos()

        tokens_brutos = self._ler_tokens_arquivo(arquivo_tokens)
        tokens = self._processar_tokens(tokens_brutos)

        handler = self._obter_handler()
        handler.calcular_firsts()
        handler.calcular_follows()

        if self.gramatica:
            analisador_ll1 = AnalisadorLL1(self.gramatica, handler)
            tabela = analisador_ll1.construir_tabela()

            parser = ParserLL1(tabela, self.gramatica)
            resultado = parser.parsear(tokens)

            if resultado and not completo:
                print("SENTENÇA ACEITA!")
                parser.imprimir_derivacao()
            elif not resultado:
                print("ERRO SINTÁTICO!")

            if completo:
                return resultado, handler, analisador_ll1, parser

            return resultado
    """
