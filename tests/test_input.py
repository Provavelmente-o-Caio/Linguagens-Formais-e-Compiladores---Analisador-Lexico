from src.analizador_lexico import AnalizadorLexico


def test_entrada_1():
    analisador_lexico = AnalizadorLexico()

    analisador_lexico.ler_entradas("tests/input_exemplo_1.txt")

    assert analisador_lexico.definicoes == {
        "id": "[a-zA-Z]([a-zA-Z] | [0-9])*",
        "num": "[1-9]([0-9])* | 0",
    }


def test_entrada_2():
    analisador_lexico = AnalizadorLexico()

    analisador_lexico.ler_entradas("tests/input_exemplo_2.txt")

    assert analisador_lexico.definicoes == {"er1": "a?(a|b)+", "er2": "b?(a|b)+"}
