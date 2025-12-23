# BSP Lot Partitioning - Python

Sistema de subdivisão automática de lotes urbanos usando **BSP (Binary Space Partitioning)**.

Migração completa do projeto Java original para Python, mantendo 100% da funcionalidade e resultados idênticos.

## 📋 Descrição

Este projeto implementa um algoritmo BSP para subdivisão recursiva de terrenos em lotes. O algoritmo:

1. Começa com um quadrilátero inicial (área disponível)
2. Subdivide recursivamente em lotes menores
3. Valida cada subdivisão (tamanho mínimo/máximo, acesso a ruas)
4. Continua até atingir o número mínimo de lotes desejado

## 🎯 Características

- ✅ **100% compatível** com a versão Java original
- ✅ **Reproduzível**: Mesma seed = mesmos resultados
- ✅ **Configurável**: Arquivo `.ini` com todos os parâmetros
- ✅ **Validação**: Garante lotes utilizáveis (não muito pequenos, não cercados)
- ✅ **Visualização**: Mostra progresso durante execução

## 📁 Estrutura do Projeto

```
bsp_erick_python/
├── point.py              # Classe Point (coordenadas 2D)
├── lot.py                # Classe Lot (lote quadrilateral)
├── lot_stack.py          # Gerenciador BSP (subdivisão recursiva)
├── java_random.py        # Gerador aleatório compatível com Java
├── config_parser.py      # Leitor de arquivos .ini
├── main.py               # Programa principal
├── backup_lot_stack.py   # Versão alternativa do LotStack
├── config_bsp.ini        # Configuração padrão
├── requirements.txt      # Dependências Python
├── .gitignore           # Arquivos ignorados pelo Git
└── README.md            # Esta documentação
```

## 🚀 Instalação

### 1. Clone o repositório

```bash
git clone <URL_DO_SEU_REPOSITORIO>
cd bsp_erick_python
```

### 2. Crie um ambiente virtual (recomendado)

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

## 📖 Como Usar

### Uso Básico

```bash
python main.py
```

### Criar Arquivo de Configuração

```bash
python main.py --create-config
```

### Opções de Linha de Comando

```bash
# Usar configuração customizada
python main.py --config meu_config.ini

# Salvar em arquivo específico
python main.py --output resultado.png

# Não mostrar janelas (apenas salvar)
python main.py --no-display

# Salvar imagens de progresso
python main.py --save-progress

# Usar matplotlib (melhor para Linux)
python main.py --use-matplotlib
```

### Exemplos Práticos

```bash
# Visualização completa com matplotlib
python main.py --use-matplotlib --save-progress

# Execução silenciosa
python main.py --no-display --output meu_resultado.png

# Config customizado + visualização
python main.py --config teste.ini --use-matplotlib
```

## ⚙️ Configuração

Edite `config_bsp.ini` para ajustar os parâmetros:

```ini
# Dimensões da imagem
IMAGE_WIDTH=1300
IMAGE_HEIGHT=1300

# Subdivisões (splits)
MIN_SPLITS_IN_X_AXIS=1
MAX_SPLITS_IN_X_AXIS=5
MIN_SPLITS_IN_Y_AXIS=1
MAX_SPLITS_IN_Y_AXIS=5

# Quantidade de lotes
MIN_AMOUNT_OF_LOTS=45

# Dimensões dos lotes (pixels)
MIN_LOT_WIDTH=125
MIN_LOT_HEIGHT=155
MAX_LOT_WIDTH=1000
MAX_LOT_HEIGHT=1000

# Quadrilátero inicial (4 vértices)
QUAD_TOP_LEFT_X=100
QUAD_TOP_LEFT_Y=200
QUAD_TOP_RIGHT_X=600
QUAD_TOP_RIGHT_Y=200
QUAD_BOTTOM_RIGHT_X=650
QUAD_BOTTOM_RIGHT_Y=1200
QUAD_BOTTOM_LEFT_X=150
QUAD_BOTTOM_LEFT_Y=1100

# Seed (mesma seed = mesmos resultados)
SEED=333
```

## 🔧 Tecnologias

- **Python 3.8+**
- **Pillow**: Manipulação de imagens
- **NumPy**: Arrays numéricos
- **Matplotlib**: Visualização (opcional, mas recomendado)

## 📊 Algoritmo BSP

### Binary Space Partitioning

O BSP divide recursivamente o espaço em regiões menores:

1. **Escolhe direção**: Horizontal ou vertical (aleatório)
2. **Subdivide**: Cria N lotes (MIN_SPLIT a MAX_SPLIT)
3. **Valida**: Tamanho mínimo + acesso a área externa
4. **Aceita/Rejeita**: Se válido, substitui pai por filhos
5. **Repete**: Até atingir MIN_LOTS

### Validações

- ✅ **Tamanho**: `largura >= MIN_WIDTH` e `altura >= MIN_HEIGHT`
- ✅ **Saída**: Lote tem acesso a áreas externas (não está cercado)

### Prioridade

- Lotes com **menor prioridade** são subdivididos primeiro (maiores)
- Prioridade aumenta a cada nível de subdivisão

## 🎓 Conceitos Implementados

### Geometria Computacional

- **Ponto em polígono**: Método das áreas de triângulos
- **Área de triângulo**: Fórmula de Shoelace
- **Verificação de conexidade**: 16 pontos ao redor de cada vértice

### Geração de Números Aleatórios

- **JavaRandom**: Implementa `java.util.Random` em Python
- **LCG**: Linear Congruential Generator
- **Reproduzibilidade**: Mesma seed = mesma sequência

## 📈 Diferenças da Versão Java

### Mantido

- ✅ Mesma lógica de subdivisão BSP
- ✅ Mesmas validações e critérios
- ✅ Mesmos resultados (bit por bit)

### Melhorias Python

- ✅ Type hints para clareza
- ✅ Documentação completa (docstrings)
- ✅ Argumentos de linha de comando
- ✅ Suporte a matplotlib (visualização estável)
- ✅ Validação de configurações

## 🐛 Troubleshooting

### Warnings do EOG (Linux)

Use `--use-matplotlib` para evitar warnings do visualizador padrão:

```bash
python main.py --use-matplotlib
```

### Não atinge MIN_LOTS

Ajuste os parâmetros no `config_bsp.ini`:
- Diminua `MIN_LOT_WIDTH` e `MIN_LOT_HEIGHT`
- Aumente `MAX_SPLIT_X` e `MAX_SPLIT_Y`

### Lotes muito irregulares

- Diminua `MAX_SPLIT_X` e `MAX_SPLIT_Y`
- Ajuste o quadrilátero inicial para forma mais regular

## 📝 Autor

- **Código Original (Java)**: Erick Oliveira Rodrigues
- **Equipe**: Ciência de Dados



## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

