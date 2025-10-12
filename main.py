from src.analizador_lexico import AnalizadorLexico


def main():
    analisador_lexico = AnalizadorLexico()

    analisador_lexico.ler_entradas("tests/input_exemplo_1.txt")

    assert analisador_lexico.definicoes == {
        "id": "[a-zA-Z]([a-zA-Z] | [0-9])*",
        "num": "[1-9]([0-9])* | 0",
    }


if __name__ == "__main__":
    main()
