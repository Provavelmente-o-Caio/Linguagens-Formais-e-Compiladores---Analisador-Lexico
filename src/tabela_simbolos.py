from typing import Dict, Optional, Tuple
from dataclasses import dataclass


class CategoriaLexica:
    """Categorias léxicas padrão para tokens.
    
    Define as categorias utilizadas para classificar tokens na
    análise léxica e na tabela de símbolos.
    """

    # Categorias usadas na tabela de símbolos
    PALAVRA_RESERVADA = "PR"
    IDENTIFICADOR = "ID"
    NUMERO_INTEIRO = "NUM_INT"
    NUMERO_REAL = "NUM_REAL"
    LITERAL = "LIT"
    
    @classmethod
    def palavra_reservada(cls, categoria: str) -> bool:
        """Verifica se categoria é palavra reservada."""
        return categoria == cls.PALAVRA_RESERVADA
    
    @classmethod
    def identificador(cls, categoria: str) -> bool:
        """Verifica se categoria é identificador."""
        return categoria == cls.IDENTIFICADOR
    
    @classmethod
    def numero(cls, categoria: str) -> bool:
        """Verifica se categoria é numérica."""
        return categoria in [cls.NUMERO_INTEIRO, cls.NUMERO_REAL]
    
    @classmethod
    def todas(cls) -> list[str]:
        """Retorna lista com todas as categorias léxicas.
        
        Returns:
            Lista de strings com todas as categorias definidas
        """
        return [
            cls.PALAVRA_RESERVADA,
            cls.IDENTIFICADOR,
            cls.NUMERO_INTEIRO,
            cls.NUMERO_REAL,
            cls.LITERAL
        ]
    
    @classmethod
    def categorias_processaveis(cls) -> list[str]:
        """Retorna categorias que devem ser processadas pela tabela de símbolos.
        
        Returns:
            Lista de tipos léxicos que entram na tabela de símbolos
        """
        return [str(cat).lower() for cat in cls.todas()]


@dataclass
class EntradaTabela:
    """Entrada na tabela de símbolos.
    
    Attributes:
        lexema: String do identificador/palavra
        categoria: Tipo léxico (PR, ID, etc.)
        posicao: Posição na tabela
        tipo: Tipo de dado (opcional, para análise semântica)
        escopo: Escopo do símbolo (opcional)
    """
    lexema: str
    categoria: str
    posicao: int
    tipo: Optional[str] = None
    escopo: Optional[str] = None
    
    def __str__(self) -> str:
        return f"<{self.lexema}, {self.categoria}, pos={self.posicao}>"


class TabelaSimbolos:
    """Tabela de símbolos para gerenciar identificadores e palavras reservadas.
    
    Implementa:
    - Busca de símbolos
    - Inserção de novos símbolos
    - Gerenciamento de palavras reservadas
    - Categorização léxica (PR, ID, etc.)
    - Se lexema já está na tabela: retorna token existente
    - Caso contrário: insere e retorna nova posição
    """
    
    def __init__(self):
        """Inicializa tabela de símbolos vazia."""
        self.tabela: Dict[str, EntradaTabela] = {}
        self.proxima_posicao: int = 0
        self.categorias = CategoriaLexica
        
    def inserir_palavra_reservada(self, lexema: str) -> EntradaTabela:
        """Insere uma palavra reservada na tabela.
        
        Args:
            lexema: Palavra reservada a inserir
            
        Returns:
            EntradaTabela com categoria PR
        """
        if lexema not in self.tabela:
            entrada = EntradaTabela(
                lexema=lexema,
                categoria=CategoriaLexica.PALAVRA_RESERVADA,
                posicao=self.proxima_posicao
            )
            self.tabela[lexema] = entrada
            self.proxima_posicao += 1
        return self.tabela[lexema]
    
    def inserir_palavras_reservadas(self, palavras: list[str]):
        for palavra in palavras:
            self.inserir_palavra_reservada(palavra)
    
    def lookup(self, lexema: str, categoria: Optional[str] = None) -> EntradaTabela:
        """Busca ou insere um símbolo na tabela.

        - Se lexema já existe: retorna entrada existente
        - Caso contrário: insere nova entrada e retorna
        
        Args:
            lexema: Símbolo a buscar/inserir
            categoria: Categoria léxica (se não especificada, usa ID)
            
        Returns:
            EntradaTabela correspondente ao símbolo
        """
        # Se já existe, retornar
        if lexema in self.tabela:
            return self.tabela[lexema]
        
        # Caso contrário, inserir novo símbolo
        categoria = categoria or CategoriaLexica.IDENTIFICADOR
        entrada = EntradaTabela(
            lexema=lexema,
            categoria=categoria,
            posicao=self.proxima_posicao
        )
        self.tabela[lexema] = entrada
        self.proxima_posicao += 1
        
        return entrada
    
    def existe(self, lexema: str) -> bool:
        return lexema in self.tabela
    
    def obter(self, lexema: str) -> Optional[EntradaTabela]:
        return self.tabela.get(lexema)
    
    def categorizar_token(self, lexema: str, tipo_lexico: str) -> Tuple[str, str]:
        """Retorna token no formato adequado:
        - Palavra reservada: <lexema, PR>
        - Identificador: <lexema, posicao>
        - Outros: <lexema, tipo>

        Args:
            lexema: String do token
            tipo_lexico: Tipo do analisador léxico (id, num, etc.)
            
        Returns:
            Tupla (lexema, categoria) para uso no parser
        """
        # Mapear tipo léxico para categoria
        categoria_map = {
            'id': CategoriaLexica.IDENTIFICADOR,
            'num': CategoriaLexica.NUMERO_INTEIRO,
            'num_int': CategoriaLexica.NUMERO_INTEIRO,
            'num_real': CategoriaLexica.NUMERO_REAL,
            'literal': CategoriaLexica.LITERAL,
        }
        
        categoria = categoria_map.get(tipo_lexico, tipo_lexico.upper())
        
        # Fazer lookup (busca ou insere)
        entrada = self.lookup(lexema, categoria)

        if CategoriaLexica.palavra_reservada(entrada.categoria):
            return (lexema, CategoriaLexica.PALAVRA_RESERVADA)
        else:
            return (lexema, str(entrada.posicao))
    
    def imprimir(self):
        """Imprime a tabela de símbolos formatada.
        
        Args:
            titulo: Título da tabela
        """
        print("Tabela de Simbolos")
        print(f"{'Pos':<5} {'Lexema':<20} {'Categoria':<10} {'Tipo':<10} {'Escopo':<10}")
    
        entradas = sorted(self.tabela.values(), key=lambda e: e.posicao)    
        for entrada in entradas:
            print(f"{entrada.posicao:<5} "
                  f"{entrada.lexema:<20} "
                  f"{entrada.categoria:<10} "
                  f"{entrada.tipo or '-':<10} "
                  f"{entrada.escopo or '-':<10}")
        
        print(f"Total de entradas: {len(self.tabela)}")
    
    def estatisticas(self) -> dict:
        """Retorna estatísticas da tabela de símbolos.
        
        Returns:
            Dicionário com contagens por categoria
        """
        stats = {}
        for entrada in self.tabela.values():
            categoria = entrada.categoria
            stats[categoria] = stats.get(categoria, 0) + 1
        return stats
    
    def limpar(self):
        """Limpa a tabela de símbolos."""
        self.tabela.clear()
        self.proxima_posicao = 0
    
    def exportar_para_dict(self) -> dict:
        """Exporta tabela para dicionário (para serialização).
        
        Returns:
            Dicionário com todas as entradas
        """
        return {
            lexema: {
                'posicao': entrada.posicao,
                'categoria': entrada.categoria,
                'tipo': entrada.tipo,
                'escopo': entrada.escopo
            }
            for lexema, entrada in self.tabela.items()
        }


__all__ = ['CategoriaLexica', 'EntradaTabela', 'TabelaSimbolos']
