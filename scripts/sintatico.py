import sys
import pandas as pd
from src.analisador_sintatico import AnalisadorSintatico
from src.slr import AnalisadorSLR, TabelaSLR


def imprimir_tabela_slr(tabela: TabelaSLR, num_estados: int):
    """Imprime a tabela SLR usando pandas DataFrame.
    
    Args:
        tabela: Tabela SLR construída
        num_estados: Número de estados da coleção canônica
    """
    # Coletar todos os terminais e não-terminais
    terminais = sorted(set(s for _, s in tabela.action.keys()), key=str)
    nao_terminais = sorted(set(nt for _, nt in tabela.goto.keys()), key=str)
    
    # Criar colunas: ACTION para cada terminal, GOTO para cada não-terminal
    colunas_action = [f"{t}" for t in terminais]
    colunas_goto = [f"{nt}" for nt in nao_terminais]
    colunas = colunas_action + colunas_goto
    
    # Criar dados da tabela
    dados = []
    for i in range(num_estados):
        linha = []
        for t in terminais:
            acao = tabela.action.get((i, t))
            linha.append(str(acao) if acao else "")
        for nt in nao_terminais:
            val = tabela.goto.get((i, nt), "")
            linha.append(str(val) if val != "" else "")
        dados.append(linha)
    
    # Criar DataFrame
    df = pd.DataFrame(dados, columns=colunas)
    df.index.name = "Estado"
    
    # Configurar pandas para mostrar todas as colunas
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    pd.set_option('display.max_colwidth', None)
    
    print("\n=== TABELA SLR ===\n")
    print(df.to_string())
    print()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python dev_sintatico.py <arquivo_gramatica>")
        sys.exit(1)
    
    arquivo = sys.argv[1]
    analisador = AnalisadorSintatico()
    analisador.ler_gramatica(arquivo)
    handler = analisador._obter_handler()
    
    # Calcular FIRST de todos os não-terminais
    print("\n=== FIRST ===")
    for nt in sorted(handler.gramatica.nao_terminais, key=lambda x: x.nome):
        first = handler.get_first(nt)
        first_str = ", ".join(sorted([str(s) for s in first]))
        print(f"FIRST({nt}) = {{ {first_str} }}")
    
    print("\n=== FOLLOW ===")
    for nt in sorted(handler.gramatica.nao_terminais, key=lambda x: x.nome):
        follow = handler.get_follow(nt)
        follow_str = ", ".join(sorted([str(s) for s in follow]))
        print(f"FOLLOW({nt}) = {{ {follow_str} }}")
    
    slr = AnalisadorSLR(analisador.gramatica, handler)
    slr.construir_colecao_canonica()
    slr.imprimir_colecao_canonica()
    
    # Construir e imprimir tabela SLR
    tabela = slr.construir_tabela()
    imprimir_tabela_slr(tabela, len(slr.colecao_canonica))
