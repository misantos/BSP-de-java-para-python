"""
lot_stack.py - Gerenciador de subdivisão BSP (Binary Space Partitioning)

Este módulo implementa o algoritmo BSP para subdivisão recursiva de lotes.
O BSP é uma técnica de particionamento espacial que divide recursivamente
um espaço em regiões menores.

Fluxo do Algoritmo:
1. Começa com um lote inicial (área total)
2. Subdivide recursivamente em lotes menores
3. Valida cada subdivisão (tamanho mínimo, acesso a ruas)
4. Continua até atingir número mínimo de lotes

Características:
- Subdivisões podem ser horizontais ou verticais (escolha aleatória)
- Cada subdivisão pode gerar N lotes (MIN_SPLIT a MAX_SPLIT)
- Lotes com menor prioridade são subdivididos primeiro (maiores primeiro)
- Validações garantem lotes utilizáveis (não muito pequenos, não cercados)

Autor: Migração Python por Claude (Original Java: Erick Oliveira Rodrigues)
"""

from collections import deque
from typing import Deque
import math
from lot import Lot, SpatialIndex
from point import Point
from java_random import JavaRandom


class LotStack:
    """
    Gerencia a coleção de lotes e sua subdivisão recursiva usando BSP.
    
    Esta classe usa variáveis de classe (static) para manter estado global,
    permitindo que Lot.has_an_exit_to_external_area() acesse a lista de lotes.
    
    Variáveis de Classe (equivalente a 'static' do Java):
        lots: Lista de todos os lotes atuais
        MIN_LOTS: Número mínimo de lotes desejados
        random_gen: Gerador de números aleatórios (JavaRandom)
        MIN/MAX_SPLIT_X/Y: Limites de subdivisões por eixo
        MIN/MAX_HEIGHT/WIDTH_LOT: Limites de tamanho dos lotes
        draw_callback: Função para desenhar progresso (opcional)
        img: Imagem base para desenho (opcional)
        spatial_index: Índice espacial para otimização O(n²) → O(k)
    
    Fluxo de Execução:
        1. __init__: Configura variáveis e inicia subdivisão
        2. partite_lot: Subdivide um lote em N lotes menores
        3. Loop: Repete até atingir MIN_LOTS
    
    Examples:
        >>> config = {'MIN_LOTS': 50, 'SEED': 333, ...}
        >>> initial_lot = Lot(0, 0, 1000, 0, 1000, 1000, 0, 1000)
        >>> lot_stack = LotStack(initial_lot, config)
        >>> final_lots = lot_stack.get_lots()
    """
    
    # ===== Variáveis de Classe (Static) =====
    # Equivalente a variáveis 'static' do Java
    # Acessíveis globalmente como LotStack.lots, LotStack.MIN_LOTS, etc.
    
    lots: Deque[Lot] = deque()  # Lista de todos os lotes (usa deque para performance)
    MIN_LOTS: int = 0           # Número mínimo de lotes desejados
    random_gen: JavaRandom = None  # Gerador aleatório (compatível com Java)
    
    # Limites de subdivisões (quantas partes dividir em cada eixo)
    MIN_SPLIT_X: int = 0  # Mínimo de subdivisões horizontais
    MAX_SPLIT_X: int = 0  # Máximo de subdivisões horizontais
    MIN_SPLIT_Y: int = 0  # Mínimo de subdivisões verticais
    MAX_SPLIT_Y: int = 0  # Máximo de subdivisões verticais
    
    # Limites de tamanho dos lotes (em pixels)
    MIN_HEIGHT_LOT: int = 0  # Altura mínima de um lote
    MIN_WIDTH_LOT: int = 0   # Largura mínima de um lote
    MAX_HEIGHT_LOT: int = 0  # Altura máxima de um lote
    MAX_WIDTH_LOT: int = 0   # Largura máxima de um lote
    
    # Callback para visualização de progresso (opcional)
    draw_callback = None  # Função chamada a cada iteração para desenhar
    img = None            # Imagem base para desenho

    # ⚡ OTIMIZAÇÃO: Índice espacial para acelerar has_an_exit_to_external_area()
    # Reduz complexidade de O(n) para O(k) onde k ≈ 5-10 lotes próximos
    spatial_index: SpatialIndex = None
    
    def __init__(self, initial_lot: Lot, config: dict):
        """
        Inicializa o LotStack e executa o algoritmo BSP.
        
        Este construtor:
        1. Limpa lotes anteriores
        2. Configura todas as variáveis de classe
        3. Executa a subdivisão inicial
        4. Loop até atingir MIN_LOTS
        
        Args:
            initial_lot (Lot): Lote inicial (área total a subdividir)
            config (dict): Dicionário com configurações:
                - MIN_LOTS: Número mínimo de lotes
                - SEED: Semente para aleatoriedade
                - MIN_SPLIT_X/Y: Mínimo de subdivisões por eixo
                - MAX_SPLIT_X/Y: Máximo de subdivisões por eixo
                - MIN_HEIGHT/WIDTH_LOT: Tamanho mínimo dos lotes
                - MAX_HEIGHT/WIDTH_LOT: Tamanho máximo dos lotes
                - draw_callback: Função para visualização (opcional)
                - img: Imagem para desenho (opcional)
        
        Note:
            O algoritmo para quando:
            - Atinge MIN_LOTS, OU
            - Não consegue mais subdividir (lotes muito pequenos/cercados)
        
        Examples:
            >>> config = {
            ...     'MIN_LOTS': 45,
            ...     'SEED': 333,
            ...     'MIN_SPLIT_X': 1, 'MAX_SPLIT_X': 5,
            ...     'MIN_SPLIT_Y': 1, 'MAX_SPLIT_Y': 5,
            ...     'MIN_HEIGHT_LOT': 155, 'MIN_WIDTH_LOT': 125,
            ...     'MAX_HEIGHT_LOT': 1000, 'MAX_WIDTH_LOT': 1000
            ... }
            >>> lot_stack = LotStack(initial_lot, config)
        """
        # Limpa lotes de execuções anteriores
        LotStack.lots.clear()
        
        # ===== Configura Variáveis de Classe =====
        
        # Parâmetros principais
        LotStack.MIN_LOTS = config['MIN_LOTS']
        LotStack.random_gen = JavaRandom(config['SEED'])  # Usa JavaRandom para compatibilidade
        
        # Limites de subdivisões
        LotStack.MIN_SPLIT_X = config['MIN_SPLIT_X']
        LotStack.MAX_SPLIT_X = config['MAX_SPLIT_X']
        LotStack.MIN_SPLIT_Y = config['MIN_SPLIT_Y']
        LotStack.MAX_SPLIT_Y = config['MAX_SPLIT_Y']
        
        # Limites de tamanho
        LotStack.MIN_HEIGHT_LOT = config['MIN_HEIGHT_LOT']
        LotStack.MIN_WIDTH_LOT = config['MIN_WIDTH_LOT']
        LotStack.MAX_HEIGHT_LOT = config['MAX_HEIGHT_LOT']
        LotStack.MAX_WIDTH_LOT = config['MAX_WIDTH_LOT']
        
        # Visualização (opcional)
        LotStack.draw_callback = config.get('draw_callback')
        LotStack.img = config.get('img')

        # ⚡ OTIMIZAÇÃO: Inicializa índice espacial
        # Cell size otimizado: 100px funciona bem para lotes típicos de 125-1000px
        LotStack.spatial_index = SpatialIndex(cell_size=100.0)

        # ===== Inicia Subdivisão =====

        # Adiciona lote inicial ao índice espacial
        LotStack.spatial_index.add_lot(initial_lot)

        # Primeira subdivisão (lote inicial → primeiros lotes)
        LotStack.partite_lot(initial_lot)
        
        # ===== Loop Principal =====
        # Continua subdividindo até atingir MIN_LOTS
        
        while len(LotStack.lots) < LotStack.MIN_LOTS:
            # Mostra progresso no console
            print(f"Total de lotes atual: {len(LotStack.lots)}")
            
            # Encontra a prioridade mínima (lotes com menor prioridade = maiores)
            # Integer.MAX_VALUE do Java = float('inf') do Python
            min_priority = float('inf')
            
            # Desenha progresso se callback disponível
            if LotStack.draw_callback and LotStack.img:
                LotStack.draw_callback(list(LotStack.lots), LotStack.img.copy())
            
            # Calcula a menor prioridade entre todos os lotes
            for lot in LotStack.lots:
                if lot.priority < min_priority:
                    min_priority = lot.priority
            
            # ===== Seleciona Lotes para Subdividir =====
            # Subdivide SE:
            # - Prioridade == mínima (lotes maiores), OU
            # - Tamanho >= máximo (lotes muito grandes)
            
            # list() para evitar modificar durante iteração
            for lot in list(LotStack.lots):
                # Skip se: prioridade > mínima E tamanho < máximo
                # (lotes pequenos com prioridade alta não são subdivididos)
                if (lot.priority > min_priority and
                    lot.get_width() < LotStack.MAX_WIDTH_LOT and 
                    lot.get_height() < LotStack.MAX_HEIGHT_LOT):
                    continue
                
                # Tenta subdividir este lote
                LotStack.partite_lot(lot)
    
    @staticmethod
    def partite_lot(lot_to_partition: Lot) -> None:
        """
        Subdivide um lote em múltiplos lotes menores (método estático).
        
        Algoritmo:
        1. Escolhe direção: horizontal ou vertical (aleatório)
        2. Escolhe número de subdivisões: MIN_SPLIT a MAX_SPLIT (aleatório)
        3. Calcula coordenadas dos novos lotes
        4. Valida tamanho e acesso a áreas externas
        5. Se válido: remove pai, adiciona filhos
        6. Se inválido: cancela subdivisão inteira
        
        Args:
            lot_to_partition (Lot): Lote a ser subdividido
        
        Note:
            - Método estático (pode ser chamado sem instância)
            - Para se já atingiu MIN_LOTS
            - Rejeita subdivisão inteira se algum lote filho for inválido
            - Usa Math.ceil para arredondar anchor_points
        
        Validações:
            1. Tamanho: largura >= MIN_WIDTH e altura >= MIN_HEIGHT
            2. Saída: lote deve ter acesso a área externa (não cercado)
        
        Examples:
            >>> # Subdivide um lote retangular
            >>> lote = Lot(0, 0, 500, 0, 500, 500, 0, 500)
            >>> LotStack.partite_lot(lote)
            >>> # lote foi substituído por 2-5 lotes menores
        """
        # ===== Condição de Parada =====
        # Para se já atingiu o número mínimo de lotes
        if len(LotStack.lots) >= LotStack.MIN_LOTS:
            return
        
        # ===== Lista de Lotes Candidatos =====
        # Lista temporária para armazenar os novos lotes
        # Só será adicionada a LotStack.lots se TODOS forem válidos
        potential_lots = []
        
        # ===== Escolhe Direção de Subdivisão =====
        # nextBoolean() retorna True/False com 50% de chance cada
        # True = horizontal (divide verticalmente)
        # False = vertical (divide horizontalmente)
        
        if LotStack.random_gen.nextBoolean():  # ===== HORIZONTAL =====
            """
            Subdivisão Horizontal (cortes verticais):
            
            Original:          Resultado (3 subdivisões):
            +--------+         +--+--+--+
            |        |         |  |  |  |
            |        |   -->   |  |  |  |
            |        |         |  |  |  |
            +--------+         +--+--+--+
            
            Calcula vetores das bordas direita e esquerda,
            depois interpola para criar lotes intermediários.
            """
            
            # Vetores das laterais direita e esquerda
            # (de cima para baixo)
            dx_right = lot_to_partition.bottom_right.x - lot_to_partition.top_right.x
            dy_right = lot_to_partition.bottom_right.y - lot_to_partition.top_right.y
            
            dx_left = lot_to_partition.bottom_left.x - lot_to_partition.top_left.x
            dy_left = lot_to_partition.bottom_left.y - lot_to_partition.top_left.y
            
            # Quantas subdivisões fazer (aleatório entre MIN e MAX)
            # Math.ceil: arredonda para cima (garante pelo menos MIN_SPLIT)
            # nextInt(n): retorna 0 até n-1
            anchor_points = int(math.ceil(
                LotStack.MIN_SPLIT_X + 
                LotStack.random_gen.nextInt(int(LotStack.MAX_SPLIT_X - LotStack.MIN_SPLIT_X))
            ))
            
            # Cria os novos lotes
            # k varia de 1 até anchor_points (inclusive)
            for k in range(1, anchor_points + 1):
                # Pontos de início (topo do lote pai)
                ini_left_x = lot_to_partition.top_left.x
                ini_left_y = lot_to_partition.top_left.y
                ini_right_x = lot_to_partition.top_right.x
                ini_right_y = lot_to_partition.top_right.y
                
                # Cria novo lote interpolando ao longo dos vetores
                # (k-1)/anchor_points = início do lote
                # k/anchor_points = fim do lote
                new_lot = Lot(
                    # Top left
                    ini_left_x + dx_left * (k - 1) / anchor_points,
                    ini_left_y + dy_left * (k - 1) / anchor_points,
                    # Top right
                    ini_right_x + dx_right * (k - 1) / anchor_points,
                    ini_right_y + dy_right * (k - 1) / anchor_points,
                    # Bottom right
                    ini_right_x + dx_right * k / anchor_points,
                    ini_right_y + dy_right * k / anchor_points,
                    # Bottom left
                    ini_left_x + dx_left * k / anchor_points,
                    ini_left_y + dy_left * k / anchor_points
                )
                
                # Herda prioridade do pai + 1
                # Prioridade aumenta a cada nível de subdivisão
                new_lot.priority = lot_to_partition.priority + 1
                potential_lots.append(new_lot)
        
        else:  # ===== VERTICAL =====
            """
            Subdivisão Vertical (cortes horizontais):
            
            Original:          Resultado (3 subdivisões):
            +--------+         +--------+
            |        |         +--------+
            |        |   -->   +--------+
            |        |         +--------+
            +--------+         +--------+
            
            Calcula vetores das bordas superior e inferior,
            depois interpola para criar lotes intermediários.
            """
            
            # Vetores das laterais superior e inferior
            # (da esquerda para direita)
            dx_top = lot_to_partition.top_right.x - lot_to_partition.top_left.x
            dy_top = lot_to_partition.top_right.y - lot_to_partition.top_left.y
            
            dx_bottom = lot_to_partition.bottom_right.x - lot_to_partition.bottom_left.x
            dy_bottom = lot_to_partition.bottom_right.y - lot_to_partition.bottom_left.y
            
            # Quantas subdivisões fazer
            anchor_points = int(math.ceil(
                LotStack.MIN_SPLIT_Y + 
                LotStack.random_gen.nextInt(int(LotStack.MAX_SPLIT_Y - LotStack.MIN_SPLIT_Y))
            ))
            
            # Cria os novos lotes
            for k in range(1, anchor_points + 1):
                # Pontos de início (esquerda do lote pai)
                ini_top_left_x = lot_to_partition.top_left.x
                ini_top_left_y = lot_to_partition.top_left.y
                ini_bottom_left_x = lot_to_partition.bottom_left.x
                ini_bottom_left_y = lot_to_partition.bottom_left.y
                
                # Cria novo lote interpolando
                new_lot = Lot(
                    # Top left
                    ini_top_left_x + dx_top * (k - 1) / anchor_points,
                    ini_top_left_y + dy_top * (k - 1) / anchor_points,
                    # Top right
                    ini_top_left_x + dx_top * k / anchor_points,
                    ini_top_left_y + dy_top * k / anchor_points,
                    # Bottom right
                    ini_bottom_left_x + dx_bottom * k / anchor_points,
                    ini_bottom_left_y + dy_bottom * k / anchor_points,
                    # Bottom left
                    ini_bottom_left_x + dx_bottom * (k - 1) / anchor_points,
                    ini_bottom_left_y + dy_bottom * (k - 1) / anchor_points
                )
                
                new_lot.priority = lot_to_partition.priority + 1
                potential_lots.append(new_lot)
        
        # ===== Validação dos Lotes Candidatos =====
        # TODOS os lotes devem passar nas validações
        # Se algum falhar, a subdivisão inteira é cancelada
        
        for lot in potential_lots:
            # ===== Validação 1: Tamanho Mínimo =====
            # Lote deve ter largura >= MIN_WIDTH e altura >= MIN_HEIGHT
            if (lot.get_height() < LotStack.MIN_HEIGHT_LOT or 
                lot.get_width() < LotStack.MIN_WIDTH_LOT):
                # Lote muito pequeno → cancela subdivisão
                return
            
            # ===== Validação 2: Acesso a Área Externa (COM SPATIAL INDEX) =====
            # Lote deve ter pelo menos uma saída livre (não cercado)
            # Garante que lote tem acesso a ruas/áreas externas
            # ⚡ OTIMIZADO: Passa spatial_index para busca O(k) ao invés de O(n)
            if not lot.has_an_exit_to_external_area(LotStack.spatial_index):
                # Lote sem saída → cancela subdivisão
                return
        
        # ===== Subdivisão Aceita! =====
        # Todos os lotes passaram nas validações

        # ⚡ OTIMIZAÇÃO: Atualiza spatial index
        # Remove o lote pai do índice espacial
        if LotStack.spatial_index:
            LotStack.spatial_index.remove_lot(lot_to_partition)

        # Remove o lote pai da lista
        try:
            LotStack.lots.remove(lot_to_partition)
        except ValueError:
            # Lote pode já ter sido removido (não é erro)
            pass

        # Adiciona todos os lotes filhos à lista
        LotStack.lots.extend(potential_lots)

        # ⚡ OTIMIZAÇÃO: Adiciona novos lotes ao spatial index
        if LotStack.spatial_index:
            for lot in potential_lots:
                LotStack.spatial_index.add_lot(lot)
    
    def get_lots(self) -> list[Lot]:
        """
        Retorna a lista de todos os lotes finais.
        
        Returns:
            list[Lot]: Lista com todos os lotes após subdivisão
        
        Note:
            Retorna uma cópia da lista (não a deque original)
        
        Examples:
            >>> lot_stack = LotStack(initial_lot, config)
            >>> lotes_finais = lot_stack.get_lots()
            >>> print(f"Total: {len(lotes_finais)} lotes")
        """
        return list(LotStack.lots)