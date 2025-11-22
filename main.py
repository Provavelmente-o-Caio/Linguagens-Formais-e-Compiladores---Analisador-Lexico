import sys
from src.analisador_lexico import AnalisadorLexico
from src.analisador_sintatico import AnalisadorSintatico


def executar_analisador_lexico():
    """Executa analisador léxico a partir de argumentos da linha de comando."""
    if len(sys.argv) < 3:
        print("Uso: python main.py lexico <arquivo_definicoes> <arquivo_entrada> [arquivo_saida]")
        sys.exit(1)

    analisador = AnalisadorLexico()
    analisador.ler_definicoes(sys.argv[2])
    analisador.gerar_analizador()
    analisador.visualizar_automato()

    arquivo_saida = sys.argv[4] if len(sys.argv) > 4 else None
    analisador.analisar(sys.argv[3], arquivo_saida)


def executar_analisador_sintatico():
    """Executa analisador sintático a partir de argumentos da linha de comando."""
    if len(sys.argv) < 3:
        print("Uso: python main.py sintatico <arquivo_gramatica> [arquivo_palavras_reservadas]")
        sys.exit(1)

    analisador = AnalisadorSintatico()
    analisador.ler_gramatica(sys.argv[2])

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso:")
        print("  python -m main lexico <arquivo_definicoes> <arquivo_entrada> [arquivo_saida]")
        print("  python -m main sintatico <arquivo_gramatica> [arquivo_palavras_reservadas]")
        sys.exit(1)
    
    modo = sys.argv[1].lower()
    
    if modo == "lexico":
        executar_analisador_lexico()
    elif modo == "sintatico":
        executar_analisador_sintatico()
    else:
        print(f"Modo desconhecido: {modo}")
        print("Modos válidos: lexico, sintatico")
        sys.exit(1)
