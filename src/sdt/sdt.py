from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class InstrucaoTAC:
    """Instrucao de codigo de tres enderecos."""

    op: str
    arg1: Optional[str] = None
    arg2: Optional[str] = None
    resultado: Optional[str] = None

    def __str__(self) -> str:
        if self.op == "label":
            return f"{self.resultado}:"
        if self.op == "goto":
            return f"goto {self.resultado}"
        if self.op in {"ifTrue", "ifFalse"}:
            return f"{self.op} {self.arg1} goto {self.resultado}"
        if self.op == "param":
            return f"param {self.resultado}"
        if self.op == "call":
            return f"{self.resultado} = call {self.arg1}, {self.arg2}"
        if self.op == "decl":
            if self.arg2:
                return f"decl {self.arg1} {self.resultado}[{self.arg2}]"
            return f"decl {self.arg1} {self.resultado}"
        if self.op == "return":
            return "return" if self.resultado is None else f"return {self.resultado}"
        if self.op == "read":
            return f"read {self.resultado}"
        if self.op == "print":
            return f"print {self.resultado}"
        if self.op == "[]":
            return f"{self.resultado} = {self.arg1}[{self.arg2}]"
        if self.op == "[]=":
            return f"{self.arg1}[{self.arg2}] = {self.resultado}"
        if self.resultado is None:
            return f"{self.op} {self.arg1 or ''} {self.arg2 or ''}".strip()
        if self.arg2 is None:
            return f"{self.resultado} = {self.op} {self.arg1}".strip()
        return f"{self.resultado} = {self.arg1} {self.op} {self.arg2}"


@dataclass
class ValorSemantico:
    """Atributos sintetizados/herdados usados pela SDT."""

    lugar: Optional[str] = None
    codigo: List[InstrucaoTAC] = field(default_factory=list)
    verdadeiro: Optional[str] = None
    falso: Optional[str] = None
    proximo: Optional[str] = None
    inicio: Optional[str] = None
    fim: Optional[str] = None
    argumentos: List[str] = field(default_factory=list)
    tipo: Optional[str] = None


class ProgramaTAC:
    """Coletor simples de TAC com geracao de temporarios e rotulos."""

    def __init__(self) -> None:
        self.instrucoes: List[InstrucaoTAC] = []
        self._temporarios = 0
        self._rotulos = 0

    def novo_temporario(self) -> str:
        self._temporarios += 1
        return f"t{self._temporarios}"

    def novo_rotulo(self) -> str:
        self._rotulos += 1
        return f"L{self._rotulos}"

    def emitir(
        self,
        op: str,
        arg1: Optional[str] = None,
        arg2: Optional[str] = None,
        resultado: Optional[str] = None,
    ) -> InstrucaoTAC:
        instrucao = InstrucaoTAC(op=op, arg1=arg1, arg2=arg2, resultado=resultado)
        self.instrucoes.append(instrucao)
        return instrucao

    def estender(self, codigo: List[InstrucaoTAC]) -> None:
        self.instrucoes.extend(codigo)

    def texto(self) -> str:
        return "\n".join(str(instrucao) for instrucao in self.instrucoes)


class SDTConvCC2026_1:
    """Esqueleto de SDT para geracao de codigo intermediario em TAC."""

    def __init__(self) -> None:
        self.programa = ProgramaTAC()

    def combinar(self, *valores: ValorSemantico) -> ValorSemantico:
        resultado = ValorSemantico()
        for valor in valores:
            resultado.codigo.extend(valor.codigo)
        return resultado

    def literal(self, lexema: str, tipo: Optional[str] = None) -> ValorSemantico:
        return ValorSemantico(lugar=lexema, tipo=tipo)

    def identificador(self, nome: str, tipo: Optional[str] = None) -> ValorSemantico:
        return ValorSemantico(lugar=nome, tipo=tipo)

    def expressao_binaria(
        self,
        operador: str,
        esquerda: ValorSemantico,
        direita: ValorSemantico,
    ) -> ValorSemantico:
        resultado = ValorSemantico()
        resultado.codigo.extend(esquerda.codigo)
        resultado.codigo.extend(direita.codigo)
        resultado.lugar = self.programa.novo_temporario()
        resultado.codigo.append(
            InstrucaoTAC(
                op=operador,
                arg1=esquerda.lugar,
                arg2=direita.lugar,
                resultado=resultado.lugar,
            )
        )
        return resultado

    def expressao_unaria(
        self, operador: str, operando: ValorSemantico
    ) -> ValorSemantico:
        resultado = ValorSemantico()
        resultado.codigo.extend(operando.codigo)
        resultado.lugar = self.programa.novo_temporario()
        resultado.codigo.append(
            InstrucaoTAC(op=operador, arg1=operando.lugar, resultado=resultado.lugar)
        )
        return resultado

    def atribuicao(self, alvo: ValorSemantico, valor: ValorSemantico) -> ValorSemantico:
        resultado = ValorSemantico()
        resultado.codigo.extend(alvo.codigo)
        resultado.codigo.extend(valor.codigo)
        resultado.codigo.append(
            InstrucaoTAC(op="=", arg1=valor.lugar, resultado=alvo.lugar)
        )
        return resultado

    def declaracao(
        self,
        nome: str,
        tipo: str,
        dimensoes: Optional[List[int]] = None,
    ) -> ValorSemantico:
        resultado = ValorSemantico(lugar=nome, tipo=tipo)
        if dimensoes:
            resultado.argumentos = [str(dim) for dim in dimensoes]
        return resultado

    def print_stmt(self, valor: ValorSemantico) -> ValorSemantico:
        resultado = ValorSemantico()
        resultado.codigo.extend(valor.codigo)
        resultado.codigo.append(InstrucaoTAC(op="print", resultado=valor.lugar))
        return resultado

    def read_stmt(self, alvo: ValorSemantico) -> ValorSemantico:
        resultado = ValorSemantico()
        resultado.codigo.append(InstrucaoTAC(op="read", resultado=alvo.lugar))
        return resultado

    def return_stmt(self, valor: Optional[ValorSemantico] = None) -> ValorSemantico:
        resultado = ValorSemantico()
        if valor is not None:
            resultado.codigo.extend(valor.codigo)
            resultado.codigo.append(InstrucaoTAC(op="return", resultado=valor.lugar))
        else:
            resultado.codigo.append(InstrucaoTAC(op="return"))
        return resultado

    def if_sem_else(
        self, condicao: ValorSemantico, comando: ValorSemantico
    ) -> ValorSemantico:
        resultado = ValorSemantico()
        l_falso = self.programa.novo_rotulo()
        l_saida = self.programa.novo_rotulo()
        resultado.codigo.extend(condicao.codigo)
        resultado.codigo.append(
            InstrucaoTAC(op="ifFalse", arg1=condicao.lugar, resultado=l_falso)
        )
        resultado.codigo.extend(comando.codigo)
        resultado.codigo.append(InstrucaoTAC(op="goto", resultado=l_saida))
        resultado.codigo.append(InstrucaoTAC(op="label", resultado=l_falso))
        resultado.codigo.append(InstrucaoTAC(op="label", resultado=l_saida))
        return resultado

    def if_com_else(
        self,
        condicao: ValorSemantico,
        comando_verdadeiro: ValorSemantico,
        comando_falso: ValorSemantico,
    ) -> ValorSemantico:
        resultado = ValorSemantico()
        l_falso = self.programa.novo_rotulo()
        l_saida = self.programa.novo_rotulo()
        resultado.codigo.extend(condicao.codigo)
        resultado.codigo.append(
            InstrucaoTAC(op="ifFalse", arg1=condicao.lugar, resultado=l_falso)
        )
        resultado.codigo.extend(comando_verdadeiro.codigo)
        resultado.codigo.append(InstrucaoTAC(op="goto", resultado=l_saida))
        resultado.codigo.append(InstrucaoTAC(op="label", resultado=l_falso))
        resultado.codigo.extend(comando_falso.codigo)
        resultado.codigo.append(InstrucaoTAC(op="label", resultado=l_saida))
        return resultado

    def for_stmt(
        self,
        inicializacao: ValorSemantico,
        condicao: ValorSemantico,
        atualizacao: ValorSemantico,
        corpo: ValorSemantico,
    ) -> ValorSemantico:
        resultado = ValorSemantico()
        l_inicio = self.programa.novo_rotulo()
        l_fim = self.programa.novo_rotulo()
        resultado.codigo.extend(inicializacao.codigo)
        resultado.codigo.append(InstrucaoTAC(op="label", resultado=l_inicio))
        resultado.codigo.extend(condicao.codigo)
        resultado.codigo.append(
            InstrucaoTAC(op="ifFalse", arg1=condicao.lugar, resultado=l_fim)
        )
        resultado.codigo.extend(corpo.codigo)
        resultado.codigo.extend(atualizacao.codigo)
        resultado.codigo.append(InstrucaoTAC(op="goto", resultado=l_inicio))
        resultado.codigo.append(InstrucaoTAC(op="label", resultado=l_fim))
        return resultado

    def chamada_funcao(
        self, nome: str, argumentos: List[ValorSemantico]
    ) -> ValorSemantico:
        resultado = ValorSemantico()
        for argumento in argumentos:
            resultado.codigo.extend(argumento.codigo)
            resultado.codigo.append(InstrucaoTAC(op="param", resultado=argumento.lugar))
            resultado.argumentos.append(argumento.lugar or "")
        resultado.lugar = self.programa.novo_temporario()
        resultado.codigo.append(
            InstrucaoTAC(
                op="call",
                arg1=nome,
                arg2=str(len(argumentos)),
                resultado=resultado.lugar,
            )
        )
        return resultado

    def acesso_vetor(
        self, base: ValorSemantico, indice: ValorSemantico
    ) -> ValorSemantico:
        resultado = ValorSemantico()
        resultado.codigo.extend(base.codigo)
        resultado.codigo.extend(indice.codigo)
        resultado.lugar = self.programa.novo_temporario()
        resultado.codigo.append(
            InstrucaoTAC(
                op="[]", arg1=base.lugar, arg2=indice.lugar, resultado=resultado.lugar
            )
        )
        return resultado

    def texto(self) -> str:
        return self.programa.texto()
