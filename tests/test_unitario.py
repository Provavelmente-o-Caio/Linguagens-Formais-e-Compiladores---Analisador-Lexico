from src.automatos import Estado, Automato, HandlerAutomatos, EPSILON

# =====================================================
# Testes básicos do comportamento do autômato
# =====================================================


def test_processar_palavra_simples():
    q0, q1 = Estado("q0"), Estado("q1")
    a = Automato(
        estados={q0, q1},
        simbolos={"a"},
        transicoes={(q0, "a"): {q1}},
        estado_inicial=q0,
        estados_finais={q1},
    )
    assert a.processar("a") is True
    assert a.processar("") is False
    assert a.processar("aa") is False


def test_processar_com_epsilon():
    q0, q1, q2 = Estado("q0"), Estado("q1"), Estado("q2")
    a = Automato(
        estados={q0, q1, q2},
        simbolos={"a", EPSILON},
        transicoes={
            (q0, EPSILON): {q1},
            (q1, "a"): {q2},
        },
        estado_inicial=q0,
        estados_finais={q2},
    )
    # Deve aceitar "a" devido à transição ε→a
    assert a.processar("a") is True
    # Mas não deve aceitar vazio (pois ε-fecho não leva direto a final)
    assert a.processar("") is False


def test_is_deterministico():
    q0, q1, q2 = Estado("q0"), Estado("q1"), Estado("q2")
    # Determinístico
    a1 = Automato(
        {q0, q1},
        {"a"},
        {(q0, "a"): {q1}},
        q0,
        {q1},
    )
    assert a1.is_deterministico() is True

    # Não determinístico
    a2 = Automato(
        {q0, q1, q2},
        {"a", EPSILON},
        {(q0, "a"): {q1, q2}, (q1, EPSILON): {q2}},
        q0,
        {q2},
    )
    assert a2.is_deterministico() is False


# =====================================================
# Testes para os métodos do HandlerAutomatos
# =====================================================


def test_uniao_basico():
    q0, q1 = Estado("q0"), Estado("q1")
    a1 = Automato({q0, q1}, {"a"}, {(q0, "a"): {q1}}, q0, {q1})

    q2, q3 = Estado("q2"), Estado("q3")
    a2 = Automato({q2, q3}, {"b"}, {(q2, "b"): {q3}}, q2, {q3})

    handler = HandlerAutomatos()
    a_uniao = handler.uniao(a1, a2)

    assert any(estado.nome.startswith("q_uniao") for estado in a_uniao.estados)
    assert a_uniao.is_deterministico() is False
    assert a_uniao.processar("a") is True
    assert a_uniao.processar("b") is True


def test_determinizar_nfa_simples():
    q0, q1, q2 = Estado("q0"), Estado("q1"), Estado("q2")
    a = Automato(
        {q0, q1, q2},
        {"a", EPSILON},
        {(q0, "a"): {q1}, (q0, EPSILON): {q2}, (q2, "a"): {q1}},
        q0,
        {q1},
    )

    handler = HandlerAutomatos()
    dfa = handler.determinizar(a)

    assert dfa.is_deterministico() is True
    assert dfa.processar("a") is True
    assert dfa.processar("") is False


# =====================================================
# Testes para as rotinas de minimização (parciais)
# =====================================================


def test_remove_estados_inalcancaveis():
    q0, q1, q2 = Estado("q0"), Estado("q1"), Estado("q2")
    a = Automato(
        {q0, q1, q2},
        {"a"},
        {(q0, "a"): {q1}},
        q0,
        {q1},
    )
    handler = HandlerAutomatos()
    novo = handler.remove_estados_inalcancaveis(a)
    assert q2 not in novo.estados
    assert q1 in novo.estados


def test_remove_estados_mortos_detecta_bug():
    """
    Este teste é especialmente útil para depurar a função `alcanca`:
    Em algumas execuções, o código pode entrar em loop infinito
    se `alcanca` não tratar corretamente a expansão via epsilon_fecho.
    """
    q0, q1, q2 = Estado("q0"), Estado("q1"), Estado("q2")
    a = Automato(
        {q0, q1, q2},
        {"a"},
        {
            (q0, "a"): {q1},
            (q1, "a"): {q2},
        },
        q0,
        {q2},
    )
    handler = HandlerAutomatos()
    result = handler.remove_estados_mortos(a)
    assert q0 in result.estados
    assert q1 in result.estados
    assert q2 in result.estados_finais


def test_remove_estados_mortos_com_ciclo_infinito():
    """
    Teste de caso limite: um ciclo entre estados sem alcançar finais.
    O autômato é 'vivo' no sentido de transições, mas morto na aceitação.
    """
    q0, q1 = Estado("q0"), Estado("q1")
    a = Automato(
        {q0, q1},
        {"a"},
        {(q0, "a"): {q1}, (q1, "a"): {q0}},
        q0,
        set(),  # nenhum final
    )
    handler = HandlerAutomatos()
    novo = handler.remove_estados_mortos(a)
    assert len(novo.estados) == 0  # tudo deve ser removido
