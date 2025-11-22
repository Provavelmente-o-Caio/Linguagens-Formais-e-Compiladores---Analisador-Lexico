import sys

from src.cli.menu_principal import iniciar_cli
from src.analisador_lexico import AnalisadorLexico


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python main.py <arquivo_definicoes> <arquivo_entrada> [arquivo_saida]")
        sys.exit(1)

    analisador = AnalisadorLexico()
    analisador.ler_definicoes(sys.argv[1])
    analisador.gerar_analizador()
    analisador.visualizar_automato()

    arquivo_saida = sys.argv[3] if len(sys.argv) > 3 else None
    analisador.analisar(sys.argv[2], arquivo_saida)

    iniciar_cli()
