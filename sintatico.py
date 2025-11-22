import sys
from src.analisador_sintatico import AnalisadorSintatico
from src.analisadorSLR import AnalisadorSLR

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
