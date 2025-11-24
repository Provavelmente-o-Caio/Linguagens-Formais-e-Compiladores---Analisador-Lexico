from typing import Optional

from src.gramaticas import Gramatica, NaoTerminal, Terminal
from src.gramaticas.producao import Producao
from src.slr.acoes import Accept, Reduce, Shift
from src.slr.tabela_slr import TabelaSLR


class ParserSLR:
    def __init__(
        self, tabela: TabelaSLR, gramatica: Gramatica, producao_aumentada: Producao
    ) -> None:
        self.tabela: Optional[TabelaSLR] = tabela
        self.gramatica: Optional[Gramatica] = gramatica
        self.producao_aumentada = producao_aumentada  # S' ::= S

        self.historico = []
        self.derivacao = []

    def parsear(self, tokens: list[tuple[str, str]]) -> bool:
        pilha: list[int] = [0]
        simbolo: list[Terminal | NaoTerminal] = []
        entrada = [(lexema, tipo) for lexema, tipo in tokens]
        # Adicionar EOF apenas se não estiver presente
        if not entrada or entrada[-1][1] not in ["$", "EOF"]:
            entrada.append(("$", "$"))  # Fim de entrada
        posicao = 0
        self.derivacao.clear()

        # garante que a tabela foi inicializada antes de usar
        if self.tabela is None:
            raise RuntimeError(
                "Tabela SLR não inicializada. Atribua uma TabelaSLR a ParserSLR.tabela antes de chamar parsear()."
            )

        passo = 0

        while True:
            passo += 1

            # pega estado da pilha
            estado_atual: int = pilha[-1]

            # simbolo atual
            lexema_atual, tipo_atual = entrada[posicao]
            simbolo_atual = Terminal(tipo_atual)

            # consultar tabela
            chave_acao = (estado_atual, simbolo_atual)
            if chave_acao not in self.tabela.action:
                self.reportar_erro(estado_atual, simbolo_atual, lexema_atual, posicao)
                return False

            acao = self.tabela.action[chave_acao]

            if isinstance(acao, Shift):
                estado_destino = acao.estado

                simbolo.append(simbolo_atual)
                pilha.append(estado_destino)

                posicao += 1
            elif isinstance(acao, Reduce):
                numero_producao = acao.producao
                producao: Producao = self.obter_producao(numero_producao)

                tamanho_corpo: int = len(producao.corpo)

                if tamanho_corpo > 0:
                    for _ in range(tamanho_corpo):
                        simbolo.pop()
                        pilha.pop()

                estado_topo: int = pilha[-1]

                nao_terminal: NaoTerminal = producao.cabeca
                simbolo.append(nao_terminal)

                # GOTO
                chave_goto: tuple[int, NaoTerminal] = (estado_topo, nao_terminal)
                if chave_goto not in self.tabela.goto:
                    print(f"GOTO[{estado_topo}, {nao_terminal}] não definido")
                    return False

                estado_goto = self.tabela.goto[chave_goto]
                pilha.append(estado_goto)

                self.derivacao.append(str(producao))

            elif isinstance(acao, Accept):
                print("\n" + "=" * 80)
                print("✓ SENTENÇA ACEITA!")
                print("=" * 80)
                return True
            else:
                print(f"Ação desconhecida: {acao}")
                return False

    def reportar_erro(
        self, estado: int, simbolo: Terminal | NaoTerminal, lexema: str, posicao: int
    ):
        print("\n" + "=" * 80)
        print("ERRO SINTÁTICO")
        print("=" * 80)
        print(f"Posição: {posicao}")
        print(f"Token inesperado: '{lexema}' (tipo: {simbolo})")
        print(f"Estado do parser: {estado}")

        esperados = self.obter_tokens_esperados(estado)
        if esperados:
            print("\nTokens esperados:")
            for token in esperados:
                print(f"  - {token}")

        print("=" * 80)

    def obter_producao(self, numero_producao: int) -> Producao:
        if self.gramatica is None:
            raise ValueError("Gramática não inicializada")

        if numero_producao == 0 and self.producao_aumentada:
            return self.producao_aumentada

        for producao in self.gramatica.producoes:
            if producao.numero == numero_producao:
                return producao

        raise ValueError(f"Produção {numero_producao} não encontrada")

    def imprimir_derivacao(self):
        if not self.derivacao:
            print("Nenhuma derivação disponível (execute parsear() primeiro)")
            return

        print("\n=== DERIVAÇÃO (Rightmost) ===\n")
        for i, producao in enumerate(self.derivacao, 1):
            print(f"{i:3}. {producao}")

    def obter_tokens_esperados(self, estado: int) -> list[str]:
        """Retorna lista de tokens válidos para um estado."""
        if self.tabela is None:
            return []

        tokens = []
        for (s, terminal), _ in self.tabela.action.items():
            if s == estado:
                tokens.append(str(terminal))
        return sorted(set(tokens))
