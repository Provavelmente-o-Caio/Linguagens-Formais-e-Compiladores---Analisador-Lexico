from src.expressaoregular import NodoER, ExpressaoRegular
from src.automatos import Automato, Estado

EPSILON = "&"


class ConversorER_AFD:
    """
    Conversor de Expressão Regular para Autômato Finito Determinístico.
    
    Referência: Aho et al., Seção 3.9 "De uma Expressão Regular para um AFD".
    
    Implementa a construção direta de AFD a partir de ER, sem passar por AFND.
    """
    
    def gerar_afd(self, regex: ExpressaoRegular) -> Automato:
        """Gera um AFD diretamente de uma expressão regular usando o algoritmo de construção direta.
        
        Passos:
        1. Constrói árvore da ER aumentada (r).#
        2. Calcula nullable, firstpos, lastpos para cada nodo
        3. Calcula followpos para cada posição
        4. Constrói estados: cada estado é um conjunto de posições
        5. Estado inicial = firstpos(raiz)
        6. Estados finais = aqueles que contêm a posição de #
        7. Transições: δ(S, a) = ∪{followpos(p) | p ∈ S e símbolo[p] = a}
        """
        raiz: NodoER = regex.processar()
        if not raiz.firstpos:
            return Automato(
                estados={Estado("q0")},
                simbolos=set(),
                transicoes={},
                estado_inicial=Estado("q0"),
                estados_finais={Estado("q0")} if raiz.nullable else set(),
            )
        q0: frozenset[int] = frozenset(raiz.firstpos)
        estados: set[frozenset[int]] = {q0}
        marcados: set[frozenset[int]] = set()

        entradas = {
            nodo.valor
            for nodo in regex.folhas.values()
            if nodo.valor is not None and nodo.valor not in [EPSILON, "#"]
        }

        transicoes: dict[tuple[frozenset[int], str], frozenset[int]] = {}

        while estados - marcados:
            T = next(s for s in estados if s not in marcados)
            marcados.add(T)

            for a in entradas:
                U = set()
                for p in T:
                    if regex.folhas[p].valor == a:
                        U.update(regex.folhas[p].followpos)
                U = frozenset(U)

                if U and a:
                    if U not in estados:
                        estados.add(U)
                    transicoes[(T, a)] = U

        # calculo dos estados finais
        pos_hash = next(p for p, nodo in regex.folhas.items() if nodo.valor == "#")

        finais = {S for S in estados if pos_hash in S}

        # convertendo para as estruturas de dados definidas anteriormente
        mapa_estados = {S: Estado(nome=self.gerar_nomes(S)) for S in estados}

        estado_inicial = mapa_estados[q0]
        estados_finais = {mapa_estados[S] for S in finais}

        transicoes_convertidas = {
            (mapa_estados[T], a): {mapa_estados[U]} for (T, a), U in transicoes.items()
        }

        return Automato(
            estados=set(mapa_estados.values()),
            simbolos=entradas,
            transicoes=transicoes_convertidas,
            estado_inicial=estado_inicial,
            estados_finais=estados_finais,
        )

    def gerar_nomes(self, estados: frozenset[int] | None) -> str:
        """Gera nome legível para um estado composto por um conjunto de posições.
        
        Estados do AFD são identificados pelos conjuntos de posições que representam.
        
        Args:
            estados: Conjunto de posições (frozenset de inteiros) ou None.
            
        Returns:
            String representando o estado: "∅" para conjunto vazio, "{p1,p2,...}" caso contrário.
        """
        if not estados:
            return "∅"
        else:
            return "{" + ",".join(str(i) for i in sorted(estados)) + "}"
