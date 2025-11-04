import pytest
from src.automatos import Estado, Automato, Handler_Automatos


# ===========================================================
# Caso de uso 1 - Identificadores e números
# ===========================================================


def criar_automato_id():
    # id: [a-zA-Z]([a-zA-Z] | [0-9])*
    q0, q1, q2 = Estado("q0"), Estado("q1"), Estado("q2")
    simbolos = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")

    transicoes = {}
    # Primeira letra deve ser [a-zA-Z]
    for s in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ":
        transicoes[(q0, s)] = {q1}

    # Depois pode repetir letras ou números
    for s in simbolos:
        transicoes[(q1, s)] = {q1}

    return Automato({q0, q1, q2}, simbolos, transicoes, q0, {q1})


def criar_automato_num():
    # num: [1-9]([0-9])* | 0
    q0, q1, q2, q3 = Estado("q0"), Estado("q1"), Estado("q2"), Estado("q3")
    simbolos = set("0123456789")
    transicoes = {}

    # "0" isolado
    transicoes[(q0, "0")] = {q3}

    # [1-9]
    for s in "123456789":
        transicoes[(q0, s)] = {q1}
        transicoes[(q1, s)] = {q1}

    # Qualquer dígito após [1-9]
    for s in "0123456789":
        transicoes[(q1, s)] = {q1}

    return Automato({q0, q1, q2, q3}, simbolos, transicoes, q0, {q1, q3})


@pytest.fixture
def automatos_id_num():
    return criar_automato_id(), criar_automato_num()


@pytest.mark.parametrize(
    "entrada, esperado",
    [
        ("a1", ("a1", "id")),
        ("0", ("0", "num")),
        ("teste2", ("teste2", "id")),
        ("21", ("21", "num")),
        ("alpha123", ("alpha123", "id")),
        ("3444", ("3444", "num")),
        ("a43teste", ("a43teste", "id")),
    ],
)
def test_tokens_id_num(entrada, esperado, automatos_id_num):
    id_auto, num_auto = automatos_id_num
    token_esperado = esperado[1]

    if id_auto.processar(entrada):
        assert token_esperado == "id"
    elif num_auto.processar(entrada):
        assert token_esperado == "num"
    else:
        pytest.fail(f"{entrada} não reconhecido por nenhum autômato")


# ===========================================================
# Caso de uso 2 - Palavras que começam com 'a' ou 'b'
# ===========================================================


def criar_automato_er1():
    # er1: a?(a|b)+
    q0, q1 = Estado("q0"), Estado("q1")
    simbolos = {"a", "b"}
    transicoes = {
        (q0, "a"): {q1},
        (q0, "b"): {q1},
        (q1, "a"): {q1},
        (q1, "b"): {q1},
    }
    return Automato({q0, q1}, simbolos, transicoes, q0, {q1})


def criar_automato_er2():
    # er2: b?(a|b)+
    q0, q1 = Estado("q0"), Estado("q1")
    simbolos = {"a", "b"}
    transicoes = {
        (q0, "a"): {q1},
        (q0, "b"): {q1},
        (q1, "a"): {q1},
        (q1, "b"): {q1},
    }
    return Automato({q0, q1}, simbolos, transicoes, q0, {q1})


@pytest.fixture
def automatos_ab():
    return criar_automato_er1(), criar_automato_er2()


@pytest.mark.parametrize(
    "entrada, esperado",
    [
        ("aa", ("aa", "er1")),
        ("bbbba", ("bbbba", "er2")),
        ("ababab", ("ababab", "er1")),
        ("bbbbb", ("bbbbb", "er2")),
    ],
)
def test_tokens_a_b(entrada, esperado, automatos_ab):
    er1, er2 = automatos_ab
    token_esperado = esperado[1]

    if entrada.startswith("a"):
        assert er1.processar(entrada) is True
        assert token_esperado == "er1"
    elif entrada.startswith("b"):
        assert er2.processar(entrada) is True
        assert token_esperado == "er2"
    else:
        pytest.fail(f"{entrada} não reconhecido por nenhum autômato")


# ===========================================================
# Casos extras para verificar falhas conhecidas
# ===========================================================


def test_token_invalido_retorna_erro(automatos_id_num):
    id_auto, num_auto = automatos_id_num
    entrada = "@abc"

    reconhecido = id_auto.processar(entrada) or num_auto.processar(entrada)
    assert not reconhecido, "Símbolo inválido deveria causar erro léxico"


def test_uniao_lexica(automatos_id_num):
    """Simula a união dos dois AFDs e verifica se ambos os padrões funcionam."""
    handler = Handler_Automatos()
    id_auto, num_auto = automatos_id_num
    uniao = handler.uniao(id_auto, num_auto)

    assert uniao.processar("a123")
    assert uniao.processar("0")
    assert uniao.processar("9999")
    assert not uniao.processar("$")
