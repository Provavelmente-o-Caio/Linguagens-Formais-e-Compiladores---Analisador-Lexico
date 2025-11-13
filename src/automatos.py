from dataclasses import dataclass
from typing import override

EPSILON = "ε"


@dataclass(frozen=True)
class Estado:
    nome: str

    @override
    def __str__(self):
        return self.nome

    @override
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
        if len(self.estados):
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
        else:
            self.simbolos = set()
            self.transicoes = {}
            self.estado_inicial = Estado("Vazio")
            self.estados_finais = set()

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

        for (_, simbolo), _ in transicoes.items():
            if simbolo not in self.simbolos:
                self.simbolos.add(simbolo)

    def transiciona(self, estados_atuais: set[Estado], simbolo: str) -> set[Estado]:
        """
        Retorna os estados que um dado conjunto de etados alcança
        """
        # recebe set de estados para lidar com o não-determinismo
        novos_estados: set[Estado] = set()
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

    def alcanca(
        self, estados_atuais: set[Estado], estados_destino: set[Estado]
    ) -> bool:
        """
        Retorna se algum dos estados de entrada atinge algum dos estados destino
        """

        processados: set[Estado] = set()
        processando: list[Estado] = list(estados_atuais)

        while processando:
            estado_atual: Estado = processando.pop(0)

            if estado_atual in processados:
                continue

            processados.add(estado_atual)

            if estado_atual in estados_destino:
                return True

            epsilon_fecho_atual: set[Estado] = self.epsilon_fecho({estado_atual})

            for simbolo in self.simbolos:
                epsilon_fecho_atual |= self.transiciona(epsilon_fecho_atual, simbolo)

            processando.extend(epsilon_fecho_atual - processados)

        return False

    def is_deterministico(self) -> bool:
        for (_, simbolo), destinos in self.transicoes.items():
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


class HandlerAutomatos:
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
        if automato.is_deterministico():
            return automato

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
        processados: set[frozenset[Estado]] = set()

        while nao_processados:
            conjunto_atual = nao_processados.pop()

            if conjunto_atual in processados:
                continue

            processados.add(conjunto_atual)

            estado_atual = dicionario_estados[frozenset(conjunto_atual)]

            for simbolo in automato_determinizado.simbolos:
                conjunto_destino: set[Estado] = set()

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

    def remove_estados_inalcancaveis(self, automato: Automato) -> Automato:
        # utilizando a função transiciona preciso remover os estados que nunca alcanço a partir de nenhuma transição
        alcancados: set[Estado] = {automato.estado_inicial}
        processados: set[Estado] = set()
        processando: list[Estado] = [automato.estado_inicial]
        transicoes: dict[tuple[Estado, str], set[Estado]] = dict()

        while processando:
            estado_atual: Estado = processando.pop(0)
            processados.add(estado_atual)
            for simbolo in automato.simbolos:
                estados_alcancados: set[Estado] = automato.transiciona(
                    {estado_atual}, simbolo
                )
                if estados_alcancados:
                    transicoes[estado_atual, simbolo] = estados_alcancados
                    for estado_alcancado in estados_alcancados:
                        if estado_alcancado not in processados:
                            alcancados.add(estado_alcancado)
                            processando.append(estado_alcancado)

        estados_finais_alcancaveis: set[Estado] = alcancados & automato.estados_finais

        automato_alcancavel: Automato = Automato(
            alcancados,
            automato.simbolos,
            transicoes,
            automato.estado_inicial,
            estados_finais_alcancaveis,
        )

        return automato_alcancavel

    def remove_estados_mortos(self, automato: Automato) -> Automato:
        estados_vivos: set[Estado] = set()

        for estado in automato.estados:
            if automato.alcanca({estado}, automato.estados_finais):
                estados_vivos.add(estado)

        transicoes: dict[tuple[Estado, str], set[Estado]] = {}

        finais_vivos: set[Estado] = automato.estados_finais & estados_vivos

        for (origem, simbolo), destino in automato.transicoes.items():
            destino_vivo = destino & estados_vivos
            if origem in estados_vivos and destino_vivo:
                transicoes[(origem, simbolo)] = destino_vivo

        automato_vivo: Automato = Automato(
            estados_vivos,
            automato.simbolos,
            transicoes,
            automato.estado_inicial,
            finais_vivos,
        )

        return automato_vivo

    def remove_estados_equivalentes(self, automato: Automato) -> Automato:
        if not automato.is_deterministico():
            automato = self.determinizar(automato)

        if len(automato.estados) <= 1:
            return automato

        # Criação dos novos grupos
        finais: set[Estado] = automato.estados_finais
        nao_finais: set[Estado] = automato.estados - finais

        grupos: list[set[Estado]] = [finais, nao_finais] if nao_finais else [finais]
        novos_grupos: list[set[Estado]] = []
        dividindo = True

        while dividindo:
            dividindo = False

            for grupo in grupos:
                representacoes: dict[tuple[int | None, ...], set[Estado]] = {}

                for estado in grupo:
                    chave: list[int | None] = []

                    for simbolo in automato.simbolos:
                        destinos: set[Estado] = automato.transicoes.get(
                            (estado, simbolo), set()
                        )

                        if not destinos:
                            chave.append(None)
                            continue

                        destino: Estado = next(iter(destinos))

                        indice_destino: int | None = next(
                            (i for i, p in enumerate(grupos) if destino in p),
                            None,
                        )

                        chave.append(indice_destino)
                    tuple_chave: tuple[int | None, ...] = tuple(chave)

                    if tuple_chave not in representacoes:
                        representacoes[tuple_chave] = set()
                    representacoes[tuple_chave].add(estado)

                novos_grupos.extend(representacoes.values())

            if len(grupos) != len(novos_grupos):
                dividindo = True

            grupos = novos_grupos

        # Cada grupo vira um estado
        mapeamento: dict[Estado, Estado] = {}
        novos_estados: set[Estado] = set()

        for i, grupo in enumerate(grupos):
            nome_estado = "_".join(sorted(estado.nome for estado in grupo))
            estado = Estado(f"q{i}_{nome_estado}")
            novos_estados.add(estado)
            for e in grupo:
                mapeamento[e] = estado

        # Novas transicoes
        novas_transicoes: dict[tuple[Estado, str], set[Estado]] = {}
        for (origem, simbolo), destinos in automato.transicoes.items():
            nova_origem: Estado = mapeamento[origem]
            for destino in destinos:
                novo_destino = mapeamento[destino]
                novas_transicoes.setdefault((nova_origem, simbolo), set()).add(
                    novo_destino
                )

        # Finais e iniciais
        novo_inicial: Estado = mapeamento[automato.estado_inicial]
        novos_finais: set[Estado] = {mapeamento[e] for e in automato.estados_finais}

        return Automato(
            novos_estados,
            automato.simbolos,
            novas_transicoes,
            novo_inicial,
            novos_finais,
        )

    def minimizar(self, automato: Automato) -> Automato:
        automato = self.determinizar(automato)
        automato = self.remove_estados_inalcancaveis(automato)
        automato = self.remove_estados_mortos(automato)
        automato = self.remove_estados_equivalentes(automato)
        return automato

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
