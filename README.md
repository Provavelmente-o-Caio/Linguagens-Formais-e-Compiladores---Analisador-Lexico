# Linguagens-Formais-e-Compiladores---Analisador-Lexico

## Requisitos
- [ ] Conversão de expressão regular para autômato finito determinístico (Algoritmo apresentado no livro de Aho).
- [x] Minimização de autômatos.
- [x] União de Autômatos via epsilon-transição.
- [x] Determinação de Autômatos.
### Interface
- [ ] Inclusão de expressões regulares para todos os padrões de tokens, usando definições regulares.
- [ ] Para cada ER deve ser gerado um AFD correspondente.
- [ ] Os AFD devem ser minimizados e Unidos com epsilon-transições.
- [ ] O AFND resultante deve ser determinizado gerando a tabela de análise léxica (representação implícita).
- [ ] A interface de execução do analisador léxico deve permiti a entrade de um texto fonte (conjunto de palavras, sumulando um programa fonte).
- [ ] O texto fonte será analisado, utilizando a tabela de análise léxica gerada na parte de projeto, e deve grar um arquivo de saída com a lista de todos os tokens encontrados na forma <lexema, padrão> ou reportar o erro <lexema, erro!> caso a entrada não seja válida.
### Observações
- Para notacionar o epsilon use &.
- A tabela de análise deve poder ser "vizualizada".
- Os autômatos finitos gerados pela conversão das ERs também devem poder ser visualisados (arquivo ou tela - na forma de tabela).

## HowTo
1. No diretório do projeto, para executar a interface CLI, será necessário ter a lib rich instalado, para isso podemos utilizar um virtualenv e instalar a lib de forma descartável com o seguinte comando:
   ```bash
    python3 -m venv env
    . env/bin/activate
    pip install -r requirements.txt
   ```
  
    (Se por algum motivo você não possuir o venv instalado, instale com: `sudo apt install python3-venv`)

2. Em seguida, para executar o analisador léxico, basta rodar o seguinte comando:
   ```bash
   python main.py
   ```
3. Caso você queira executar o projeto de forma simples pelo VSCode, você pode selecionar o interpretador Python do virtualenv criado no passo 1, então após criar o virtualenv, abra o VSCode no diretório do projeto e selecione o interpretador com `Ctrl + Shift + P` e digitando `Python: Select Interpreter`, então escolha o interpretador dentro da pasta `env/bin/python`.