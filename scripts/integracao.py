#!/usr/bin/env python3
import sys
from pathlib import Path
from src.analisador_lexico import AnalisadorLexico
from src.analisador_sintatico import AnalisadorSintatico


def main():
    # Arquivos de entrada
    arquivo_definicoes = "./tests/integracao/definicao_com_dot.txt"
    arquivo_gramatica = "./tests/integracao/gramatica_com_dot.txt"
    arquivo_fonte = "./tests/integracao/fonte_com_dot.txt"
    arquivo_tokens = "./tests/integracao/tokens_saida.txt"
    
    print("\n[FASE 1] ANÁLISE LÉXICA")
    lexico = AnalisadorLexico()
    lexico.ler_definicoes(arquivo_definicoes)
    lexico.gerar_analisador()

    with open(arquivo_fonte, 'r') as f:
        lexico.entrada_texto = f.readlines()
    
    tokens = lexico.analisar()
    lexico.salvar_tokens(tokens, arquivo_tokens)
    

    print("[FASE 2] ANÁLISE SINTÁTICA")
    sintatico = AnalisadorSintatico()
    sintatico.ler_gramatica(arquivo_gramatica)
    
    resultado = sintatico.analisar(arquivo_tokens)
    if resultado:
        sintatico.tabela_simbolos.imprimir()

        stats = sintatico.tabela_simbolos.estatisticas()
        print("\nEstatísticas:")
        print(stats)


if __name__ == "__main__":
    sys.exit(main())
