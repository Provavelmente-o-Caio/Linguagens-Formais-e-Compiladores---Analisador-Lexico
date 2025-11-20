# from src.analizador_lexico import AnalizadorLexico
from src.cli.menu_principal import iniciar_cli

def main():
    # analisador_lexico = AnalizadorLexico()

    # analisador_lexico.ler_entradas("tests/input_exemplo_1.txt")

    # assert analisador_lexico.definicoes == {
    #     "id": "[a-zA-Z]([a-zA-Z] | [0-9])*",
    #     "num": "[1-9]([0-9])* | 0",
    # }
    iniciar_cli()


if __name__ == "__main__":
    main()
