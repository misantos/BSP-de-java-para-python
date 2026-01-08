"""
point.py - Classe Point para representar coordenadas 2D

Autor: Refatoração Python
Data: 2026-01-07
"""

from typing import Tuple
import math


class Point:
    """Representa um ponto 2D com coordenadas x e y."""
    
    def __init__(self, x: float, y: float):
        self.x = float(x)
        self.y = float(y)
    
    def __repr__(self) -> str:
        return f"Point({self.x:.2f}, {self.y:.2f})"
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Point):
            return False
        return abs(self.x - other.x) < 1e-6 and abs(self.y - other.y) < 1e-6
    
    def __hash__(self) -> int:
        return hash((round(self.x, 6), round(self.y, 6)))
    
    def distance_to(self, other: 'Point') -> float:
        """Calcula distância euclidiana até outro ponto."""
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)
    
    def midpoint(self, other: 'Point') -> 'Point':
        """Retorna ponto médio entre este ponto e outro."""
        return Point((self.x + other.x) / 2, (self.y + other.y) / 2)
    
    def as_tuple(self) -> Tuple[float, float]:
        """Retorna coordenadas como tupla."""
        return (self.x, self.y)
    
    def as_int_tuple(self) -> Tuple[int, int]:
        """Retorna coordenadas como tupla de inteiros."""
        return (int(round(self.x)), int(round(self.y)))
    
    def translate(self, dx: float, dy: float) -> 'Point':
        """Retorna novo ponto transladado."""
        return Point(self.x + dx, self.y + dy)
    
    def interpolate(self, other: 'Point', t: float) -> 'Point':
        """
        Interpola entre este ponto e outro.
        
        Args:
            other: Ponto destino
            t: Fator de interpolação (0.0 = self, 1.0 = other)
            
        Returns:
            Ponto interpolado
        """
        return Point(
            self.x + (other.x - self.x) * t,
            self.y + (other.y - self.y) * t
        )


# Teste do módulo
if __name__ == "__main__":
    p1 = Point(0, 0)
    p2 = Point(10, 10)
    
    print(f"P1: {p1}")
    print(f"P2: {p2}")
    print(f"Distância: {p1.distance_to(p2):.2f}")
    print(f"Ponto médio: {p1.midpoint(p2)}")
    print(f"Interpolação 0.25: {p1.interpolate(p2, 0.25)}")
    print(f"Interpolação 0.75: {p1.interpolate(p2, 0.75)}")