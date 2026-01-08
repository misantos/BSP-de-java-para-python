"""
lot.py - Classe Lot para representar lotes quadrilaterais

Autor: Refatoração Python
Data: 2026-01-07
"""

from typing import List, Optional, TYPE_CHECKING
from point import Point

if TYPE_CHECKING:
    from spatial_index import SpatialIndex


class Lot:
    """
    Representa um lote quadrilateral com 4 vértices.
    
    Estrutura dos vértices:
        top_left ─────────── top_right
           │                    │
           │                    │
           │                    │
        bottom_left ────── bottom_right
    """
    
    def __init__(self, x1: float, y1: float, x2: float, y2: float,
                 x3: float, y3: float, x4: float, y4: float):
        """
        Cria um lote com 4 vértices.
        
        Args:
            x1, y1: Coordenadas do top_left
            x2, y2: Coordenadas do top_right
            x3, y3: Coordenadas do bottom_right
            x4, y4: Coordenadas do bottom_left
        """
        self.top_left = Point(x1, y1)
        self.top_right = Point(x2, y2)
        self.bottom_right = Point(x3, y3)
        self.bottom_left = Point(x4, y4)
        self.priority = 0  # Prioridade para subdivisão (0 = maior prioridade)
    
    def __repr__(self) -> str:
        return (f"Lot(TL={self.top_left}, TR={self.top_right}, "
                f"BR={self.bottom_right}, BL={self.bottom_left})")
    
    def get_width(self) -> float:
        """
        Retorna a largura média do lote.
        Média entre a largura superior e inferior.
        """
        top_width = self.top_left.distance_to(self.top_right)
        bottom_width = self.bottom_left.distance_to(self.bottom_right)
        return (top_width + bottom_width) / 2
    
    def get_height(self) -> float:
        """
        Retorna a altura média do lote.
        Média entre a altura esquerda e direita.
        """
        left_height = self.top_left.distance_to(self.bottom_left)
        right_height = self.top_right.distance_to(self.bottom_right)
        return (left_height + right_height) / 2
    
    def get_area(self) -> float:
        """
        Calcula a área do quadrilátero usando a fórmula Shoelace.
        """
        # Usando Shoelace formula para polígono
        points = [self.top_left, self.top_right, self.bottom_right, self.bottom_left]
        n = len(points)
        area = 0.0
        
        for i in range(n):
            j = (i + 1) % n
            area += points[i].x * points[j].y
            area -= points[j].x * points[i].y
        
        return abs(area) / 2.0
    
    def get_center(self) -> Point:
        """Retorna o centro do lote."""
        cx = (self.top_left.x + self.top_right.x + 
              self.bottom_right.x + self.bottom_left.x) / 4
        cy = (self.top_left.y + self.top_right.y + 
              self.bottom_right.y + self.bottom_left.y) / 4
        return Point(cx, cy)
    
    def get_vertices(self) -> List[Point]:
        """Retorna lista com os 4 vértices."""
        return [self.top_left, self.top_right, self.bottom_right, self.bottom_left]
    
    def get_bounding_box(self) -> tuple:
        """
        Retorna bounding box do lote.
        
        Returns:
            (min_x, min_y, max_x, max_y)
        """
        xs = [self.top_left.x, self.top_right.x, self.bottom_right.x, self.bottom_left.x]
        ys = [self.top_left.y, self.top_right.y, self.bottom_right.y, self.bottom_left.y]
        return (min(xs), min(ys), max(xs), max(ys))
    
    @staticmethod
    def triangle_area(p1: Point, p2: Point, p3: Point) -> float:
        """
        Calcula área de um triângulo usando a fórmula do determinante.
        """
        return abs(
            (p1.x * (p2.y - p3.y) + 
             p2.x * (p3.y - p1.y) + 
             p3.x * (p1.y - p2.y)) / 2.0
        )
    
    def is_inside(self, p: Point) -> bool:
        """
        Verifica se um ponto está dentro do quadrilátero.
        Usa o método de comparação de áreas.
        
        Se a soma das áreas dos 4 triângulos formados com o ponto
        for igual à área do quadrilátero, o ponto está dentro.
        """
        # Área total do quadrilátero
        quad_area = (
            self.triangle_area(self.top_left, self.top_right, self.bottom_right) +
            self.triangle_area(self.top_left, self.bottom_left, self.bottom_right)
        )
        
        # Soma das áreas dos 4 triângulos formados com o ponto p
        area1 = self.triangle_area(p, self.top_left, self.top_right)
        area2 = self.triangle_area(p, self.top_right, self.bottom_right)
        area3 = self.triangle_area(p, self.bottom_right, self.bottom_left)
        area4 = self.triangle_area(p, self.bottom_left, self.top_left)
        
        total_area_with_p = area1 + area2 + area3 + area4
        
        # Se áreas iguais (com margem de erro), ponto está dentro
        return abs(total_area_with_p - quad_area) < 1.0  # Margem de 1 pixel
    
    def has_an_exit_to_external_area(self, spatial_index: Optional['SpatialIndex'] = None,
                                      all_lots: Optional[List['Lot']] = None) -> bool:
        """
        Verifica se o lote tem saída para área externa.
        Testa 16 pontos ao redor dos 4 vértices.
        
        Args:
            spatial_index: Índice espacial para otimizar busca (opcional)
            all_lots: Lista de todos os lotes (alternativa ao spatial_index)
            
        Returns:
            True se pelo menos um ponto de teste está livre
        """
        SPREAD = 8  # Distância de teste em pixels
        
        # Testa 4 pontos ao redor de cada vértice
        test_points = []
        for vertex in self.get_vertices():
            test_points.extend([
                Point(vertex.x - SPREAD, vertex.y - SPREAD),
                Point(vertex.x + SPREAD, vertex.y + SPREAD),
                Point(vertex.x + SPREAD, vertex.y - SPREAD),
                Point(vertex.x - SPREAD, vertex.y + SPREAD),
            ])
        
        for test_point in test_points:
            is_blocked = False
            
            # Pega lotes para verificar
            if spatial_index:
                lots_to_check = spatial_index.get_nearby_lots(test_point)
            elif all_lots:
                lots_to_check = all_lots
            else:
                # Sem lista de lotes, assume que tem saída
                return True
            
            # Verifica se o ponto está dentro de algum outro lote
            for other_lot in lots_to_check:
                if other_lot is self:
                    continue
                if other_lot.is_inside(test_point):
                    is_blocked = True
                    break
            
            # Se encontrou um ponto livre, tem saída!
            if not is_blocked:
                return True
        
        # Todos os 16 pontos bloqueados = sem saída
        return False
    
    def copy(self) -> 'Lot':
        """Retorna uma cópia do lote."""
        new_lot = Lot(
            self.top_left.x, self.top_left.y,
            self.top_right.x, self.top_right.y,
            self.bottom_right.x, self.bottom_right.y,
            self.bottom_left.x, self.bottom_left.y
        )
        new_lot.priority = self.priority
        return new_lot


# Teste do módulo
if __name__ == "__main__":
    # Cria lote retangular simples
    lot = Lot(0, 0, 100, 0, 100, 50, 0, 50)
    
    print(f"Lote: {lot}")
    print(f"Largura: {lot.get_width():.2f}")
    print(f"Altura: {lot.get_height():.2f}")
    print(f"Área: {lot.get_area():.2f}")
    print(f"Centro: {lot.get_center()}")
    print(f"Bounding box: {lot.get_bounding_box()}")
    
    # Testa ponto dentro/fora
    p_inside = Point(50, 25)
    p_outside = Point(150, 25)
    
    print(f"\nPonto {p_inside} está dentro: {lot.is_inside(p_inside)}")
    print(f"Ponto {p_outside} está dentro: {lot.is_inside(p_outside)}")