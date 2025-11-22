import re

import time
from src.automatos import Automato, Estado, HandlerAutomatos
from src.conversorER import ConversorER_AFD
from src.expressaoregular import ExpressaoRegular


class AnalisadorLexico:
    def __init__(self):
        self.conversor: ConversorER_AFD = ConversorER_AFD()
        self.handler_automatos: HandlerAutomatos = HandlerAutomatos()
        self.definicoes: dict[str, str] = {}
        self.automato_unificado: Automato | None = None
        self.mapa_estados_padroes: dict[Estado, str] = {}

    def ler_grupos(self, expressao: str) -> str:
        """
        Lê expresoes que foram entradas no formato de grupos, como [a-z], [A-Z], [a-zA-Z], [0-9]
        """
        resultado: str = expressao
        padrao = r"\[([^\]]+)\]"

        resultado = re.sub(padrao, self.expandir_match, resultado)

        return resultado

    def expandir_match(self, match):
        conteudo = match.group(1)
        caracteres = self.processar_grupos(conteudo)

        if not caracteres:
            raise ValueError(f"Grupo vazio ou inválido: [{conteudo}]")

        # Gerar união: (a|b|c|...)
        return f"({('|'.join(caracteres))})"

    def processar_grupos(self, conteudo: str) -> list[str]:
        caracteres = []
        i = 0

        while i < len(conteudo):
            # Verifica se é um range (x-y)
            if i + 2 < len(conteudo) and conteudo[i + 1] == "-":
                inicio = conteudo[i]
                fim = conteudo[i + 2]

                # Expandir range
                caracteres.extend(self.expandir_caracter(inicio, fim))
                i += 3  # Pula início, '-', e fim
            else:
                # Caractere individual
                caracteres.append(conteudo[i])
                i += 1

        return caracteres

    def expandir_caracter(self, inicio: str, fim: str) -> list[str]:
        inicio_letra = inicio.isalpha()
        fim_letra = fim.isalpha()
        inicio_digito = inicio.isdigit()
        fim_digito = fim.isdigit()

        if inicio_letra and not fim_letra:
            raise ValueError(
                f"Range inválido: '{inicio}-{fim}' "
                f"('{inicio}' é letra, mas '{fim}' não é)"
            )

        if inicio_digito and not fim_digito:
            raise ValueError(
                f"Range inválido: '{inicio}-{fim}' "
                f"('{inicio}' é dígito, mas '{fim}' não é)"
            )

        if not inicio_letra and not inicio_digito:
            raise ValueError(
                f"Range inválido: '{inicio}-{fim}' ('{inicio}' não é letra nem dígito)"
            )

        if not fim_letra and not fim_digito:
            raise ValueError(
                f"Range inválido: '{inicio}-{fim}' ('{fim}' não é letra nem dígito)"
            )

        # Validar ordem
        if ord(inicio) > ord(fim):
            raise ValueError(
                f"Range inválido: '{inicio}-{fim}' ('{inicio}' vem depois de '{fim}')"
            )

        return [chr(i) for i in range(ord(inicio), ord(fim) + 1)]

    def ler_definicoes(self, arquivo: str):
        with open(arquivo, "r") as f:
            for num_linha, linha in enumerate(f, 1):
                linha = linha.strip()
                # comentários
                if linha.startswith("#"):
                    continue

                if ":" not in linha:
                    raise ValueError(
                        f"Linha {num_linha} com formato inválido"
                        f"Esperava 'nome:expressao', obteve: {linha}"
                    )

                nome, er = linha.split(":")
                nome = nome.strip()
                er = er.strip()

                if not nome:
                    raise ValueError(
                        f"Linha {num_linha} com nome vazio"
                        f"Esperava 'nome:expressao', obteve: {linha}"
                    )
                if not er:
                    raise ValueError(
                        f"Linha {num_linha} com expressão regular vazia"
                        f"Esperava 'nome:expressao', obteve: {linha}"
                    )

                er = self.ler_grupos(er)

                self.definicoes[nome] = er
                print(f"Nova definição: {nome} = {er}")

    def gerar_analizador(self):
        """
        Gerar um autômato unificado a partir das definições
        """
        if not self.definicoes:
            raise ValueError("Nenhuma definição foi adicionada")

        afds_minimizados: list[Automato] = []

        for idx, (nome, expressao) in enumerate(self.definicoes.items()):
            print(f"usando a definição de {nome}: {expressao}")

            try:
                t0 = time.time()
                er = ExpressaoRegular(expressao)
                t1 = time.time()
                print(f"1/4 Parse: {t1 - t0}")
                t0 = time.time()
                afd = self.conversor.gerar_afd(er)
                t1 = time.time()
                print(f"2/4 Gerar AFD: {t1 - t0}")

                t0 = time.time()
                afd = self.handler_automatos.minimizar(afd)
                t1 = time.time()
                print(f"3/4 Minimizar: {t1 - t0}")

                t0 = time.time()
                afd_renomeado = self.renomear_estados_afd(afd, f"{nome}_")
                t1 = time.time()
                print(f"4/4 Renomear: {t1 - t0}")

                for estado in afd_renomeado.estados_finais:
                    self.mapa_estados_padroes[estado] = nome

                afds_minimizados.append(afd_renomeado)
            except Exception as e:
                print(f"Erro ao gerar AFD para {nome}: {e}")
                raise

        # Unindo os AFDs
        automato_unido = afds_minimizados[0]
        for afd in afds_minimizados[1:]:
            automato_unido = self.handler_automatos.uniao(automato_unido, afd)

        automato_unido, mapeamento = self.handler_automatos.determinizar_com_mapeamento(
            automato_unido
        )
        self.atualizar_mapeamento(mapeamento)

        self.automato_unificado = automato_unido

    def renomear_estados_afd(self, afd: Automato, prefixo: str) -> Automato:
        # Criar mapeamento de estados antigos para novos
        mapeamento = {}
        for estado in afd.estados:
            novo_nome = f"{prefixo}{estado.nome}"
            mapeamento[estado] = Estado(novo_nome)

        # Criar novas transições
        novas_transicoes = {}
        for (origem, simbolo), destinos in afd.transicoes.items():
            nova_origem = mapeamento[origem]
            novos_destinos = {mapeamento[d] for d in destinos}
            novas_transicoes[(nova_origem, simbolo)] = novos_destinos

        # Criar novo autômato
        return Automato(
            estados=set(mapeamento.values()),
            simbolos=afd.simbolos.copy(),
            transicoes=novas_transicoes,
            estado_inicial=mapeamento[afd.estado_inicial],
            estados_finais={mapeamento[e] for e in afd.estados_finais},
        )

    def analisar(
        self, arquivo: str, arquivo_saida: str | None = None
    ) -> list[tuple[str, str]]:
        tokens: list[tuple[str, str]] = []
        with open(arquivo, "r") as f:
            for num_linha, linha in enumerate(f, 1):
                linha = linha.strip()

                if linha.startswith("#") or not linha:
                    continue

                palavras = linha.split()

                for palavra in palavras:
                    token = self.tokenizar(palavra)
                    tokens.append(token)
                    print(f"<{token[0]}, {token[1]}>")

        if arquivo_saida:
            with open(arquivo_saida, "w") as f:
                for token in tokens:
                    f.write(f"{token[0]} -> {token[1]}\n")
            print(f"Tokens salvos em {arquivo_saida}")

        return tokens

    def tokenizar(self, palavra: str):
        estado_atual = self.automato_unificado.estado_inicial

        ultimo_estado_final = None
        ultima_posicao_valida = -1

        for i, simbolo in enumerate(palavra):
            proximo = self.automato_unificado.transicoes.get(
                (estado_atual, simbolo), set()
            )

            if not proximo:
                break

            # relíquia de usar o mesmo modelo para AFD e AFND, como temos só um estado o primeiro sempre será ele
            estado_atual = next(iter(proximo))

            if estado_atual in self.automato_unificado.estados_finais:
                ultimo_estado_final = estado_atual
                ultima_posicao_valida = i

        if ultimo_estado_final and ultima_posicao_valida == len(palavra) - 1:
            padrao = self.mapa_estados_padroes.get(ultimo_estado_final, "desconhecido")
            return palavra, padrao
        else:
            return palavra, "erro!"

    def atualizar_mapeamento(self, mapeamento: dict[Estado, frozenset[Estado]]):
        novo_mapa = {}

        for estado_determinizado, conjunto_original in mapeamento.items():
            tokens_possiveis = []
            for estado_original in conjunto_original:
                if estado_original in self.mapa_estados_padroes:
                    token = self.mapa_estados_padroes[estado_original]
                    if token not in tokens_possiveis:
                        tokens_possiveis.append(token)

            if tokens_possiveis:
                padrao_escolhido = None

                for nome in self.definicoes.keys():
                    if nome in tokens_possiveis:
                        padrao_escolhido = nome
                        break

                if padrao_escolhido is None:
                    padrao_escolhido = tokens_possiveis[0]

                if len(tokens_possiveis) > 1:
                    print(f"  Estado {estado_determinizado.nome}:")
                    print(f"    Padrões possíveis: {tokens_possiveis}")
                    print(f"    Escolhido (prioridade): {padrao_escolhido}")

                novo_mapa[estado_determinizado] = padrao_escolhido

        self.mapa_estados_padroes = novo_mapa

    def visualizar_automato(self):
        if not self.automato_unificado:
            print("Nenhum automato foi gerado")
            return

        self.handler_automatos.print_tabela(self.automato_unificado)
