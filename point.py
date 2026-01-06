"""
Classe Point - Representa um ponto 2D no plano cartesiano.

Este módulo define a classe Point, que representa um ponto no plano cartesiano.
É usada para armazenar as coordenadas dos vértices dos lotes quadrilaterais.
"""

import math


class Point:
    """Representa um ponto 2D com coordenadas x e y.
    
    Esta classe é usada para representar os vértices dos lotes quadrilaterais
    no algoritmo BSP. Cada lote possui 4 pontos (topLeft, topRight, bottomLeft, bottomRight).
    
    Attributes:
        x (float): Coordenada x do ponto (horizontal)
        y (float): Coordenada y do ponto (vertical)
    
    Examples:
        >>> p1 = Point(10, 20)
        >>> p2 = Point(30, 40)
        >>> distancia = p1.distance_to(p2)
    """
    
    def __init__(self, x: float = 0.0, y: float = 0.0):
        """
        Inicializa um ponto.
        
        Args:
            x: Coordenada x (padrão: 0.0)
            y: Coordenada y (padrão: 0.0)
        """
        self.x = x
        self.y = y
    
    def __repr__(self) -> str:
        """Retorna representação string do ponto.
        Returns:
            str: String no formato "Point(x, y)"
        """
        return f"Point({self.x}, {self.y})"
    
    def __eq__(self, other) -> bool:
        """Verifica igualdade entre dois pontos."""
        if not isinstance(other, Point):
            return False
        return self.x == other.x and self.y == other.y
    
    def distance_to(self, other: 'Point') -> float:
        """Calcula distância euclidiana até outro ponto."""
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)