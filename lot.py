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
    
    def has_an_exit_to_external_area(self) -> bool:
        """
        Verifica se o lote tem pelo menos uma saída para área externa.
        
        Um lote precisa ter acesso a áreas externas (ruas) para ser válido.
        Este método verifica se o lote está completamente cercado por outros lotes.
        
        Algoritmo:
        1. Para cada vértice do lote, testa 4 direções ao redor (8 pixels de distância)
        2. Se algum ponto testado NÃO está dentro de outro lote, há uma saída
        3. Se todos os pontos estão bloqueados, o lote não tem saída
        
        Returns:
            bool: True se há pelo menos uma saída livre, False se está completamente cercado
        
        Note:
            - Acessa LotStack.lots diretamente (variável de classe estática)
            - SPREAD = 8 pixels: distância para testar ao redor dos vértices
            - Testa 16 pontos no total (4 vértices × 4 direções)
        
        Examples:
            >>> # Um lote isolado sempre tem saída
            >>> lote = Lot(0, 0, 100, 0, 100, 100, 0, 100)
            >>> lote.has_an_exit_to_external_area()
            True
        """
        # Import aqui para evitar dependência circular
        from lot_stack import LotStack
        
        lot = self
        SPREAD = 8
        
        # Inicializa todas as direções como True (livres)
        top_left_top_left = True
        top_left_bottom_right = True
        top_left_bottom_left = True
        top_left_top_right = True
        
        top_right_top_left = True
        top_right_bottom_right = True
        top_right_bottom_left = True
        top_right_top_right = True
        
        bottom_left_top_left = True
        bottom_left_bottom_right = True
        bottom_left_top_right = True
        bottom_left_bottom_left = True
        
        bottom_right_top_left = True
        bottom_right_top_right = True
        bottom_right_bottom_left = True
        bottom_right_bottom_right = True
        
        # Verifica se os vértices estão dentro de algum outro lote
        for it_lot in LotStack.lots:
            if it_lot == lot:
                continue
            
            # topLeft
            if it_lot.is_inside(Point(lot.top_left.x - SPREAD, lot.top_left.y - SPREAD)):
                top_left_top_left = False
            if it_lot.is_inside(Point(lot.top_left.x + SPREAD, lot.top_left.y + SPREAD)):
                top_left_bottom_right = False
            if it_lot.is_inside(Point(lot.top_left.x + SPREAD, lot.top_left.y - SPREAD)):
                top_left_top_right = False
            if it_lot.is_inside(Point(lot.top_left.x - SPREAD, lot.top_left.y + SPREAD)):
                top_left_bottom_left = False
            
            # topRight
            if it_lot.is_inside(Point(lot.top_right.x - SPREAD, lot.top_right.y - SPREAD)):
                top_right_top_left = False
            if it_lot.is_inside(Point(lot.top_right.x + SPREAD, lot.top_right.y + SPREAD)):
                top_right_bottom_right = False
            if it_lot.is_inside(Point(lot.top_right.x + SPREAD, lot.top_right.y - SPREAD)):
                top_right_top_right = False
            if it_lot.is_inside(Point(lot.top_right.x - SPREAD, lot.top_right.y + SPREAD)):
                top_right_bottom_left = False
            
            # bottomLeft
            if it_lot.is_inside(Point(lot.bottom_left.x - SPREAD, lot.bottom_left.y - SPREAD)):
                bottom_left_top_left = False
            if it_lot.is_inside(Point(lot.bottom_left.x + SPREAD, lot.bottom_left.y + SPREAD)):
                bottom_left_bottom_right = False
            if it_lot.is_inside(Point(lot.bottom_left.x + SPREAD, lot.bottom_left.y - SPREAD)):
                bottom_left_top_right = False
            if it_lot.is_inside(Point(lot.bottom_left.x - SPREAD, lot.bottom_left.y + SPREAD)):
                bottom_left_bottom_left = False
            
            # bottomRight
            if it_lot.is_inside(Point(lot.bottom_right.x - SPREAD, lot.bottom_right.y - SPREAD)):
                bottom_right_top_left = False
            if it_lot.is_inside(Point(lot.bottom_right.x + SPREAD, lot.bottom_right.y + SPREAD)):
                bottom_right_bottom_right = False
            if it_lot.is_inside(Point(lot.bottom_right.x + SPREAD, lot.bottom_right.y - SPREAD)):
                bottom_right_top_right = False
            if it_lot.is_inside(Point(lot.bottom_right.x - SPREAD, lot.bottom_right.y + SPREAD)):
                bottom_right_bottom_left = False
        
        # Se qualquer direção está livre, retorna True
        return (top_left_top_left or
                top_left_top_right or
                top_left_bottom_left or
                top_left_bottom_right or
                
                top_right_top_left or
                top_right_top_right or
                top_right_bottom_left or
                top_right_bottom_right or
                
                bottom_right_top_left or
                bottom_right_top_right or
                bottom_right_bottom_left or
                bottom_right_bottom_right or
                
                bottom_left_top_left or
                bottom_left_top_right or
                bottom_left_bottom_left or
                bottom_left_bottom_right)
    
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