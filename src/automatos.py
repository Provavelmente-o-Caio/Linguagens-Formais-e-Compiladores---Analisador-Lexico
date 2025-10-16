from dataclasses import dataclass


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

    def adicionar_transicoes(
        self, transicoes: dict[tuple[Estado, str], set[Estado]]
    ) -> None:
        self.transicoes.update(transicoes)

        for (estado_origem, simbolo), estado_destino in transicoes.items():
            if simbolo not in self.simbolos:
                self.simbolos.add(simbolo)

    def transiciona(self, estado_atual: Estado) -> set[Estado]:
        pass

    def processar(self, palavra: str) -> bool:
        pass

    def print_tabela(self):
        # Ordenar estados e símbolos para apresentação consistente
        estados_ord = sorted(self.estados, key=lambda e: e.nome)
        simbolos_ord = sorted(self.simbolos)

        # Calcular largura das colunas
        largura_estado = max(len(str(e.nome)) for e in estados_ord)
        largura_estado = max(largura_estado, len("Estado"))

        larguras_simbolos = {}
        for s in simbolos_ord:
            max_len = len(s)
            for e in estados_ord:
                destinos = self.transicoes.get((e, s), set())
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
            if estado == self.estado_inicial:
                marcador += "→"
            if estado in self.estados_finais:
                marcador += "*"

            nome_estado = f"{marcador}{estado.nome}"
            linha = f"{nome_estado:<{largura_estado}} | "

            transicoes_linha = []
            for s in simbolos_ord:
                destinos = self.transicoes.get((estado, s), set())
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
