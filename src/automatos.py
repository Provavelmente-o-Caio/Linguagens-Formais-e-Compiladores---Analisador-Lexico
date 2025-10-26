from dataclasses import dataclass

EPSILON = "ε"


@dataclass(frozen=True)
class Estado:
    nome: str

    def __str__(self):
        return self.nome

    def __repr__(self):
        return f"Estado({self.nome!r})"


class Automato:
    def __init__(
        self,
        estados: set[Estado],
        simbolos: set[str],
        transicoes: dict[tuple[Estado, str], set[Estado]],
        estado_inicial: Estado,
        estados_finais: set[Estado],
    ):
        self.estados: set[Estado] = set(estados)
        self.simbolos: set[str] = set(simbolos)
        self.transicoes: dict[tuple[Estado, str], set[Estado]] = (
            transicoes  # caso seja possível implementar não determinismo
        )
        self.estado_inicial: Estado = estado_inicial
        self.estados_finais: set[Estado] = set(estados_finais)

        # Validações:
        if self.estado_inicial not in self.estados:
            raise ValueError("Estado inicial é desconhecido")
        if not self.estados_finais.issubset(estados):
            raise ValueError("Algum dos estados finais é desconhecido")
        for (s, a), dests in self.transicoes.items():
            if s not in self.estados:
                raise ValueError(f"transição de estado desconhecido: {s}")
            if a not in self.simbolos:
                raise ValueError(f"símbolo da transição desconhecido: {a}")
            if not set(dests).issubset(self.estados):
                raise ValueError(
                    "destinos da transição contêm estado(s) desconhecido(s)"
                )

    def adicionar_estados(self, estados_novos: set[Estado]) -> None:
        self.estados.update(estados_novos)

    def adicionar_estados_finais(self, estados_finais_novos: set[Estado]) -> None:
        if not estados_finais_novos.issubset(self.estados):
            raise ValueError("Algum dos estados finais é desconhecido")

        self.estados_finais.update(estados_finais_novos)

    def adicionar_transicoes(
        self, transicoes: dict[tuple[Estado, str], set[Estado]]
    ) -> None:
        self.transicoes.update(transicoes)

        for (estado_origem, simbolo), estado_destino in transicoes.items():
            if simbolo not in self.simbolos:
                self.simbolos.add(simbolo)

    def transiciona(self, estados_atuais: set[Estado], simbolo: str) -> set[Estado]:
        # recebe set de estados para lidar com o não-determinismo
        novos_estados = set()
        for e in estados_atuais:
            novos_estados.update(self.transicoes.get((e, simbolo), set()))
        return novos_estados

    def processar(self, palavra: str) -> bool:
        estados_atuais = self.epsilon_fecho({self.estado_inicial})
        for simbolo in palavra:
            estados_atuais = self.epsilon_fecho(
                self.transiciona(estados_atuais, simbolo)
            )
        return any(estado in self.estados_finais for estado in estados_atuais)

    def is_deterministico(self) -> bool:
        for (estado, simbolo), destinos in self.transicoes.items():
            if len(destinos) > 1 or simbolo == EPSILON:
                return False
        return True

    def epsilon_fecho(self, estados: set[Estado]) -> set[Estado]:
        estados_alcancaveis = set(estados)
        estados_a_processar = list(estados)
        while estados_a_processar:
            atual = estados_a_processar.pop()
            for novo_estado in self.transiciona({atual}, EPSILON):
                if novo_estado not in estados_alcancaveis:
                    estados_alcancaveis.add(novo_estado)
                    estados_a_processar.append(novo_estado)
        return estados_alcancaveis


class Handler_Automatos:
    def uniao(self, automato1: Automato, automato2: Automato) -> Automato:
        nomes_existentes = {e.nome for e in automato1.estados | automato2.estados}
        i = 0
        while f"q_uniao_{i}" in nomes_existentes:
            i += 1
        qnovo = Estado(f"q_uniao_{i}")
        automato_uniao = Automato({qnovo}, set(), {}, qnovo, set())

        automato_uniao.adicionar_estados(automato1.estados)
        automato_uniao.adicionar_estados(automato2.estados)

        automato_uniao.adicionar_transicoes(automato1.transicoes)
        automato_uniao.adicionar_transicoes(automato2.transicoes)

        automato_uniao.adicionar_transicoes(
            {
                (qnovo, EPSILON): {automato1.estado_inicial, automato2.estado_inicial},
            }
        )

        automato_uniao.adicionar_estados_finais(automato1.estados_finais)
        automato_uniao.adicionar_estados_finais(automato2.estados_finais)

        automato_uniao.simbolos.update(automato1.simbolos)
        automato_uniao.simbolos.update(automato2.simbolos)

        return automato_uniao

    def junta_nome_estados(self, estados: set[Estado]):
        return "".join(sorted(e.nome for e in estados))

    def determinizar(self, automato: Automato) -> Automato:
        conjunto_inicial_novo: set[Estado] = automato.epsilon_fecho(
            {automato.estado_inicial}
        )
        q_inicial_novo: Estado = Estado(self.junta_nome_estados(conjunto_inicial_novo))

        dicionario_estados: dict[frozenset[Estado], Estado] = {
            frozenset(conjunto_inicial_novo): q_inicial_novo
        }

        automato_determinizado: Automato = Automato(
            {q_inicial_novo}, automato.simbolos - {EPSILON}, {}, q_inicial_novo, set()
        )

        nao_processados: list[frozenset[Estado]] = [frozenset(conjunto_inicial_novo)]
        processados: set[set[Estado]] = set()

        while nao_processados:
            conjunto_atual = nao_processados.pop()

            if conjunto_atual in processados:
                continue
            processados.add(conjunto_atual)

            estado_atual = dicionario_estados[frozenset(conjunto_atual)]

            for simbolo in automato_determinizado.simbolos:
                conjunto_destino = set()

                for estado_afd in conjunto_atual:
                    destinos = automato.transicoes.get((estado_afd, simbolo), set())
                    conjunto_destino.update(destinos)

                conjunto_destino = automato.epsilon_fecho(conjunto_destino)

                if not conjunto_destino:
                    continue

                if frozenset(conjunto_destino) not in dicionario_estados:
                    estado_novo = Estado(self.junta_nome_estados(conjunto_destino))
                    dicionario_estados[frozenset(conjunto_destino)] = estado_novo

                    automato_determinizado.adicionar_estados({estado_novo})
                    nao_processados.append(frozenset(conjunto_destino))

                estado_destino = dicionario_estados[frozenset(conjunto_destino)]

                automato_determinizado.adicionar_transicoes(
                    {(estado_atual, simbolo): {estado_destino}}
                )

        for conjunto, estado in dicionario_estados.items():
            if any(e in automato.estados_finais for e in conjunto):
                automato_determinizado.adicionar_estados_finais({estado})

        return automato_determinizado

    def print_tabela(self, automato: Automato):
        # Ordenar estados e símbolos para apresentação consistente
        estados_ord = sorted(automato.estados, key=lambda e: e.nome)
        simbolos_ord = sorted(automato.simbolos)

        # Calcular largura das colunas
        largura_estado = max(len(str(e.nome)) for e in estados_ord)
        largura_estado = max(largura_estado, len("Estado"))

        larguras_simbolos = {}
        for s in simbolos_ord:
            max_len = len(s)
            for e in estados_ord:
                destinos = automato.transicoes.get((e, s), set())
                if destinos:
                    destinos_str = ", ".join(sorted(str(d.nome) for d in destinos))
                    max_len = max(max_len, len(destinos_str))
            larguras_simbolos[s] = max(max_len, 3)

        # Imprimir cabeçalho
        print("\nTabela de Transição:")
        print(
            "="
            * (
                largura_estado
                + sum(larguras_simbolos.values())
                + len(simbolos_ord) * 3
                + 1
            )
        )

        header = f"{'Estado':<{largura_estado}} | "
        header += " | ".join(f"{s:^{larguras_simbolos[s]}}" for s in simbolos_ord)
        print(header)
        print(
            "-"
            * (
                largura_estado
                + sum(larguras_simbolos.values())
                + len(simbolos_ord) * 3
                + 1
            )
        )

        # Imprimir linhas de transição
        for estado in estados_ord:
            # Marcar estado inicial com -> e finais com *
            marcador = ""
            if estado == automato.estado_inicial:
                marcador += "→"
            if estado in automato.estados_finais:
                marcador += "*"

            nome_estado = f"{marcador}{estado.nome}"
            linha = f"{nome_estado:<{largura_estado}} | "

            transicoes_linha = []
            for s in simbolos_ord:
                destinos = automato.transicoes.get((estado, s), set())
                if destinos:
                    destinos_str = ", ".join(sorted(str(d.nome) for d in destinos))
                    transicoes_linha.append(f"{destinos_str:^{larguras_simbolos[s]}}")
                else:
                    transicoes_linha.append(f"{'-':^{larguras_simbolos[s]}}")

            linha += " | ".join(transicoes_linha)
            print(linha)

        print(
            "="
            * (
                largura_estado
                + sum(larguras_simbolos.values())
                + len(simbolos_ord) * 3
                + 1
            )
        )
        print("\nLegenda: -> = estado inicial, * = estado final, - = sem transição")
