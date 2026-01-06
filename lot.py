"""
Classe Lot - Representa um lote quadrilateral que pode ser subdividido.
Usado no algoritmo BSP (Binary Space Partitioning).

Este módulo define a classe Lot, que representa um lote de terreno como
um quadrilátero definido por 4 vértices. Inclui métodos para:

- Calcular dimensões (largura, altura)
- Verificar se um ponto está dentro do lote (geometria computacional)
- Verificar se o lote tem saída para área externa (não está cercado)

Usado no algoritmo BSP (Binary Space Partitioning) para subdivisão de terrenos.
"""

from point import Point
from typing import Set, Tuple, TYPE_CHECKING
from collections import defaultdict

if TYPE_CHECKING:
    from typing import DefaultDict


class SpatialIndex:
    """
    Índice espacial baseado em grade para acelerar consultas de proximidade.

    Divide o espaço em células de grade e mantém um mapeamento de quais lotes
    ocupam cada célula. Isso reduz a complexidade de O(n) para ~O(1) na média
    para encontrar lotes próximos a um ponto.

    Attributes:
        cell_size (float): Tamanho de cada célula da grade em pixels
        grid: Mapeamento de células para conjuntos de lotes
        lot_cells: Mapeamento de lotes para conjuntos de células que ocupam

    Examples:
        >>> index = SpatialIndex(cell_size=100.0)
        >>> index.add_lot(some_lot)
        >>> nearby = index.get_nearby_lots(Point(500, 500))
    """

    def __init__(self, cell_size: float = 50.0):
        """
        Inicializa o índice espacial.

        Args:
            cell_size: Tamanho de cada célula da grade em pixels (padrão: 50.0)
        """
        self.cell_size = cell_size
        self.grid: defaultdict[Tuple[int, int], Set['Lot']] = defaultdict(set)
        self.lot_cells: defaultdict['Lot', Set[Tuple[int, int]]] = defaultdict(set)

    def _get_cell(self, x: float, y: float) -> Tuple[int, int]:
        """
        Retorna a célula da grade para um ponto.

        Args:
            x: Coordenada x do ponto
            y: Coordenada y do ponto

        Returns:
            Tupla (cell_x, cell_y) identificando a célula
        """
        return (int(x // self.cell_size), int(y // self.cell_size))

    def _get_cells_for_lot(self, lot: 'Lot') -> Set[Tuple[int, int]]:
        """
        Retorna todas as células que um lote ocupa.

        Calcula o bounding box do lote e determina todas as células
        que o lote pode ocupar, incluindo uma margem de segurança.

        Args:
            lot: O lote para calcular células

        Returns:
            Conjunto de tuplas (cell_x, cell_y) que o lote ocupa
        """
        # Pega bounding box do lote
        min_x = min(lot.top_left.x, lot.top_right.x, lot.bottom_left.x, lot.bottom_right.x)
        max_x = max(lot.top_left.x, lot.top_right.x, lot.bottom_left.x, lot.bottom_right.x)
        min_y = min(lot.top_left.y, lot.top_right.y, lot.bottom_left.y, lot.bottom_right.y)
        max_y = max(lot.top_left.y, lot.top_right.y, lot.bottom_left.y, lot.bottom_right.y)

        # Adiciona margem para garantir que pegamos células adjacentes
        margin = self.cell_size
        min_x -= margin
        max_x += margin
        min_y -= margin
        max_y += margin

        # Calcula células que o lote ocupa
        cells = set()
        cell_min = self._get_cell(min_x, min_y)
        cell_max = self._get_cell(max_x, max_y)

        for i in range(cell_min[0], cell_max[0] + 1):
            for j in range(cell_min[1], cell_max[1] + 1):
                cells.add((i, j))

        return cells

    def add_lot(self, lot: 'Lot') -> None:
        """
        Adiciona um lote ao índice espacial.

        Args:
            lot: Lote a ser adicionado
        """
        cells = self._get_cells_for_lot(lot)
        for cell in cells:
            self.grid[cell].add(lot)
            self.lot_cells[lot].add(cell)

    def remove_lot(self, lot: 'Lot') -> None:
        """
        Remove um lote do índice espacial.

        Args:
            lot: Lote a ser removido
        """
        if lot in self.lot_cells:
            for cell in self.lot_cells[lot]:
                self.grid[cell].discard(lot)
            del self.lot_cells[lot]

    def get_nearby_lots(self, point: Point) -> Set['Lot']:
        """
        Retorna lotes próximos a um ponto.

        Verifica a célula do ponto e as 8 células adjacentes (3x3 grid)
        para encontrar todos os lotes que podem estar próximos.

        Args:
            point: Ponto de referência

        Returns:
            Conjunto de lotes próximos ao ponto
        """
        cell = self._get_cell(point.x, point.y)
        nearby = set()
        # Verifica célula atual e células adjacentes (grid 3x3)
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                nearby.update(self.grid.get((cell[0] + dx, cell[1] + dy), set()))
        return nearby

    def clear(self) -> None:
        """Limpa completamente o índice."""
        self.grid.clear()
        self.lot_cells.clear()

    def rebuild(self, lots: list['Lot']) -> None:
        """
        Reconstrói o índice com uma nova lista de lotes.

        Args:
            lots: Lista de lotes para indexar
        """
        self.clear()
        for lot in lots:
            self.add_lot(lot)


class Lot:
    """
    Representa um lote quadrilateral definido por 4 vértices.
    
    Cada lote é um quadrilátero (não necessariamente regular) que pode ser:
    - Subdividido em lotes menores (BSP)
    - Testado para verificar se pontos estão dentro dele
    - Verificado para garantir que tem acesso a áreas externas (ruas)
    
    Attributes:
        top_left (Point): Vértice superior esquerdo
        top_right (Point): Vértice superior direito
        bottom_right (Point): Vértice inferior direito
        bottom_left (Point): Vértice inferior esquerdo
        priority (int): Prioridade do lote no BSP (0 = maior, aumenta a cada subdivisão)
    
    Examples:
        >>> # Criar um lote retangular 100x200
        >>> lote = Lot(0, 0, 100, 0, 100, 200, 0, 200)
        >>> altura = lote.get_height()  # 200
        >>> largura = lote.get_width()  # 100
    """
    
    def __init__(self, x1: float = 0, y1: float = 0, 
                 x2: float = 0, y2: float = 0,
                 x3: float = 0, y3: float = 0, 
                 x4: float = 0, y4: float = 0):
        """
        Inicializa um lote quadrilateral.
        
        Args:
            x1, y1: Coordenadas do vértice superior esquerdo (topLeft)
            x2, y2: Coordenadas do vértice superior direito (topRight)
            x3, y3: Coordenadas do vértice inferior direito (bottomRight)
            x4, y4: Coordenadas do vértice inferior esquerdo (bottomLeft)
        """
        self.top_left = Point(x1, y1)
        self.top_right = Point(x2, y2)
        self.bottom_right = Point(x3, y3)
        self.bottom_left = Point(x4, y4)
        self.priority = 0
    
    def get_height(self) -> float:
        """
        Calcula a altura do lote.
        
        Como o lote pode ser irregular (trapézio, paralelogramo), calcula
        a altura máxima entre todas as combinações possíveis de lados verticais.
        
        Returns:
            float: Altura máxima do lote em pixels
        
        Examples:
            >>> lote = Lot(0, 0, 100, 0, 100, 200, 0, 200)
            >>> lote.get_height()
            200.0
        """
        return max(
            max(self.bottom_left.y - self.top_left.y, 
                self.bottom_right.y - self.top_right.y),
            max(self.bottom_left.y - self.top_right.y, 
                self.bottom_right.y - self.top_left.y)
        )
    
    def get_width(self) -> float:
        """
        Calcula a largura do lote.
        
        Como o lote pode ser irregular, calcula a largura máxima entre
        todas as combinações possíveis de lados horizontais.
        
        Returns:
            float: Largura máxima do lote em pixels
        
        Examples:
            >>> lote = Lot(0, 0, 100, 0, 100, 200, 0, 200)
            >>> lote.get_width()
            100.0
        """
        return max(
            max(self.top_right.x - self.top_left.x, 
                self.bottom_right.x - self.bottom_left.x),
            max(self.bottom_right.x - self.top_left.x, 
                self.top_right.x - self.bottom_left.x)
        )
    
    def triangle_area(self, a: Point, b: Point, c: Point) -> float:
        """
        Calcula a área de um triângulo dados 3 pontos.
        
        Usa a fórmula da área com coordenadas cartesianas (fórmula de Shoelace):
        Area = |x1(y2-y3) + x2(y3-y1) + x3(y1-y2)| / 2
        
        Args:
            a, b, c (Point): Os 3 vértices do triângulo
            
        Returns:
            float: Área do triângulo
        
        Note:
            Método auxiliar usado por is_inside() para verificar se um ponto
            está dentro do quadrilátero.
        
        Examples:
            >>> lote = Lot()
            >>> p1, p2, p3 = Point(0,0), Point(4,0), Point(0,3)
            >>> lote.triangle_area(p1, p2, p3)
            6.0
        """
        return abs((a.x * (b.y - c.y) + 
                   b.x * (c.y - a.y) + 
                   c.x * (a.y - b.y)) / 2.0)
    
    def is_inside(self, p: Point) -> bool:
        """
        Verifica se um ponto está dentro do quadrilátero.
        
        Usa o método de comparação de áreas:
        1. Calcula a área total do quadrilátero (dividido em 2 triângulos)
        2. Calcula a soma das áreas dos 4 triângulos formados pelo ponto p com cada lado
        3. Se as áreas são iguais (com margem de erro), o ponto está dentro
        
        Args:
            p (Point): Ponto a ser testado
            
        Returns:
            bool: True se o ponto está dentro do quadrilátero, False caso contrário
        
        Note:
            Usa margem de erro de 1e-6 para lidar com imprecisão de ponto flutuante.
        
        Examples:
            >>> lote = Lot(0, 0, 100, 0, 100, 100, 0, 100)
            >>> lote.is_inside(Point(50, 50))  # Centro do lote
            True
            >>> lote.is_inside(Point(150, 150))  # Fora do lote
            False
        """
        # Área total do quadrilátero (dividido em 2 triângulos)
        quad_area = (self.triangle_area(self.top_left, self.top_right, self.bottom_right) +
                    self.triangle_area(self.top_left, self.bottom_left, self.bottom_right))
        
        # Soma das áreas dos triângulos formados com o ponto p
        area1 = self.triangle_area(p, self.top_left, self.top_right)
        area2 = self.triangle_area(p, self.top_right, self.bottom_right)
        area3 = self.triangle_area(p, self.bottom_right, self.bottom_left)
        area4 = self.triangle_area(p, self.bottom_left, self.top_left)
        
        total_area_with_p = area1 + area2 + area3 + area4
        
        # Margem de erro para precisão de ponto flutuante
        return abs(total_area_with_p - quad_area) < 1e-6
    
    def has_an_exit_to_external_area(self, spatial_index: SpatialIndex = None) -> bool:
        """
        Verifica se o lote tem pelo menos uma saída para área externa (OTIMIZADO).

        Um lote precisa ter acesso a áreas externas (ruas) para ser válido.
        Este método verifica se o lote está completamente cercado por outros lotes.

        Algoritmo OTIMIZADO:
        1. Para cada vértice do lote, testa 4 direções ao redor (8 pixels de distância)
        2. Usa spatial index (se fornecido) para verificar apenas lotes próximos
        3. Se algum ponto testado NÃO está dentro de outro lote, há uma saída
        4. Se todos os pontos estão bloqueados, o lote não tem saída

        Args:
            spatial_index: Índice espacial para acelerar buscas (opcional)
                          Se None, usa LotStack.lots (comportamento original O(n))
                          Se fornecido, usa busca otimizada O(k) onde k ≈ constante

        Returns:
            bool: True se há pelo menos uma saída livre, False se está completamente cercado

        Note:
            - SPREAD = 8 pixels: distância para testar ao redor dos vértices
            - Testa 16 pontos no total (4 vértices × 4 direções)
            - Com spatial_index: O(k) onde k é número de lotes próximos (~5-10)
            - Sem spatial_index: O(n) onde n é número total de lotes (fallback)

        Examples:
            >>> # Uso com spatial index (OTIMIZADO)
            >>> index = SpatialIndex()
            >>> lote = Lot(0, 0, 100, 0, 100, 100, 0, 100)
            >>> lote.has_an_exit_to_external_area(index)
            True

            >>> # Uso sem spatial index (compatibilidade)
            >>> lote.has_an_exit_to_external_area()
            True
        """
        lot = self
        SPREAD = 8

        # Define os 16 pontos de teste (4 vértices × 4 direções)
        test_points = [
            # topLeft
            Point(lot.top_left.x - SPREAD, lot.top_left.y - SPREAD),
            Point(lot.top_left.x + SPREAD, lot.top_left.y + SPREAD),
            Point(lot.top_left.x + SPREAD, lot.top_left.y - SPREAD),
            Point(lot.top_left.x - SPREAD, lot.top_left.y + SPREAD),
            # topRight
            Point(lot.top_right.x - SPREAD, lot.top_right.y - SPREAD),
            Point(lot.top_right.x + SPREAD, lot.top_right.y + SPREAD),
            Point(lot.top_right.x + SPREAD, lot.top_right.y - SPREAD),
            Point(lot.top_right.x - SPREAD, lot.top_right.y + SPREAD),
            # bottomLeft
            Point(lot.bottom_left.x - SPREAD, lot.bottom_left.y - SPREAD),
            Point(lot.bottom_left.x + SPREAD, lot.bottom_left.y + SPREAD),
            Point(lot.bottom_left.x + SPREAD, lot.bottom_left.y - SPREAD),
            Point(lot.bottom_left.x - SPREAD, lot.bottom_left.y + SPREAD),
            # bottomRight
            Point(lot.bottom_right.x - SPREAD, lot.bottom_right.y - SPREAD),
            Point(lot.bottom_right.x + SPREAD, lot.bottom_right.y + SPREAD),
            Point(lot.bottom_right.x + SPREAD, lot.bottom_right.y - SPREAD),
            Point(lot.bottom_right.x - SPREAD, lot.bottom_right.y + SPREAD),
        ]

        # Verifica cada ponto de teste
        for test_point in test_points:
            is_blocked = False

            # Obtém lotes para verificar
            if spatial_index:
                # ⚡ OTIMIZADO: Verifica apenas lotes próximos usando spatial index
                # Reduz de O(n) para O(k) onde k ≈ 5-10 lotes próximos
                lots_to_check = spatial_index.get_nearby_lots(test_point)
            else:
                # 🐌 FALLBACK: Verifica todos os lotes (comportamento original)
                # O(n) - mais lento, mas mantém compatibilidade
                from lot_stack import LotStack
                lots_to_check = LotStack.lots

            # Verifica se o ponto está dentro de algum lote próximo
            for it_lot in lots_to_check:
                if it_lot == lot:
                    continue
                if it_lot.is_inside(test_point):
                    is_blocked = True
                    break

            # Se encontrou um ponto livre, o lote tem saída
            if not is_blocked:
                return True

        # Todos os pontos estão bloqueados
        return False
    
    def __repr__(self) -> str:
        """Retorna representação string do lote para debug.
        
        Returns:
            str: String descrevendo os 4 vértices e prioridade do lote
        
        Examples:
            >>> lote = Lot(0, 0, 100, 0, 100, 100, 0, 100)
            >>> print(lote)
            Lot(topLeft=Point(0, 0), topRight=Point(100, 0), ...)
        
        """
        return (f"Lot(topLeft={self.top_left}, topRight={self.top_right}, "
                f"bottomRight={self.bottom_right}, bottomLeft={self.bottom_left}, "
                f"priority={self.priority})")