class Estado:
    def __init__(self, nome: str, aceita: bool, inicial: bool):
        self.nome = nome
        self.aceita = aceita
        self.inicial = inicial


class Automato:
    def __init__(self):
        self.estados: set(Estado) = set()
        self.simbolos: set(str) = set()
        self.trasicoes: dict[
            tuple(Estado, str), set(Estado)
        ] = {}  # caso seja possível implementar não determinismo
        # self.trasicoes: dict[tuple(Estado, str), Estado] = {} # caso seja impossível implementar não determinismo
        self.estado_inicial = set()
        self.estados_finais = set()
