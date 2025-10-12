from src.conversorER import ConversorER


class AnalizadorLexico:
    def __init__(self):
        self.conversor: ConversorER = ConversorER()
        self.definicoes: dict[str, str] = {}

    def ler_entradas(self, arquivo: str):
        with open(arquivo, "r", encoding="utf-8") as f:
            for linha in f:
                linha = linha.strip()
                if not linha or linha.startswith("#"):
                    continue

                if ":" in linha:
                    nome, er = linha.split(":", 1)
                    self.definicoes[nome.strip()] = er.strip()
                    print(f"Adicionando {nome}: {er}")
