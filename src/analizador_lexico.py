from src.conversorER import ConversorER
import string


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

    def lida_range(self, trecho: str):
        """
        Transforma o trecho em seu formato equivalente
        """
        if trecho == "[a-z]":
            return string.ascii_lowercase

        if trecho == "[A-Z]":
            return string.ascii_uppercase

        if trecho == "[a-zA-Z]":
            return string.ascii_letters

        if trecho == "[0-9]":
            return "0123456789"
