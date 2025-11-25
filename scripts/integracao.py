#!/usr/bin/env python3
import sys
from pathlib import Path
from src.analisador_lexico import AnalisadorLexico
from src.analisador_sintatico import AnalisadorSintatico


def main():
    conjunto_testes = sys.argv[1] if len(sys.argv) > 1 else 1
    # Arquivos de entrada (usando nomenclatura numerada)
    arquivo_definicoes = f"./tests/arquivos_definicao/definicao{conjunto_testes}.txt"
    arquivo_gramatica = f"./tests/arquivos_gramatica/gramatica{conjunto_testes}.txt"
    arquivo_fonte = f"./tests/arquivos_entrada/fonte{conjunto_testes}.txt"
    arquivo_tokens = f"./tests/arquivos_saida_tokens/tokens{conjunto_testes}.txt"
    
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
