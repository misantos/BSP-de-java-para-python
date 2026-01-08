"""
spatial_index.py - Índice espacial para busca otimizada de lotes

Implementa uma grade de células para encontrar rapidamente
lotes próximos a um ponto, evitando verificar todos os lotes.

Autor: Refatoração Python
Data: 2026-01-07
"""

from typing import List, Dict, Set, Tuple, TYPE_CHECKING
from collections import defaultdict

if TYPE_CHECKING:
    from lot import Lot
    from point import Point


class SpatialIndex:
    """
    Índice espacial baseado em grade para busca rápida de lotes.
    
    Divide o espaço em células de tamanho fixo. Cada lote é 
    registrado nas células que seu bounding box toca.
    """
    
    def __init__(self, cell_size: float = 100.0):
        """
        Inicializa o índice espacial.
        
        Args:
            cell_size: Tamanho de cada célula em pixels
        """
        self.cell_size = cell_size
        self.cells: Dict[Tuple[int, int], Set['Lot']] = defaultdict(set)
        self.lot_to_cells: Dict[int, List[Tuple[int, int]]] = {}
    
    def _get_cell_coords(self, x: float, y: float) -> Tuple[int, int]:
        """Converte coordenadas para índice de célula."""
        return (int(x // self.cell_size), int(y // self.cell_size))
    
    def _get_cells_for_lot(self, lot: 'Lot') -> List[Tuple[int, int]]:
        """Retorna todas as células que um lote toca."""
        min_x, min_y, max_x, max_y = lot.get_bounding_box()
        
        cells = []
        cell_min = self._get_cell_coords(min_x, min_y)
        cell_max = self._get_cell_coords(max_x, max_y)
        
        for cx in range(cell_min[0], cell_max[0] + 1):
            for cy in range(cell_min[1], cell_max[1] + 1):
                cells.append((cx, cy))
        
        return cells
    
    def add_lot(self, lot: 'Lot') -> None:
        """
        Adiciona um lote ao índice espacial.
        
        Args:
            lot: Lote a ser adicionado
        """
        lot_id = id(lot)
        
        # Se já existe, remove primeiro
        if lot_id in self.lot_to_cells:
            self.remove_lot(lot)
        
        # Encontra células que o lote toca
        cells = self._get_cells_for_lot(lot)
        
        # Registra lote em cada célula
        for cell in cells:
            self.cells[cell].add(lot)
        
        # Guarda referência das células para remoção rápida
        self.lot_to_cells[lot_id] = cells
    
    def remove_lot(self, lot: 'Lot') -> None:
        """
        Remove um lote do índice espacial.
        
        Args:
            lot: Lote a ser removido
        """
        lot_id = id(lot)
        
        if lot_id not in self.lot_to_cells:
            return
        
        # Remove lote de todas as células
        for cell in self.lot_to_cells[lot_id]:
            if cell in self.cells:
                self.cells[cell].discard(lot)
                # Limpa célula se ficou vazia
                if not self.cells[cell]:
                    del self.cells[cell]
        
        # Remove referência
        del self.lot_to_cells[lot_id]
    
    def get_nearby_lots(self, point: 'Point', radius: float = None) -> List['Lot']:
        """
        Retorna lotes próximos a um ponto.
        
        Args:
            point: Ponto de referência
            radius: Raio de busca (opcional, usa 1 célula se None)
            
        Returns:
            Lista de lotes nas células próximas
        """
        if radius is None:
            radius = self.cell_size
        
        center_cell = self._get_cell_coords(point.x, point.y)
        cells_to_check = int(radius / self.cell_size) + 1
        
        nearby_lots = set()
        
        for dx in range(-cells_to_check, cells_to_check + 1):
            for dy in range(-cells_to_check, cells_to_check + 1):
                cell = (center_cell[0] + dx, center_cell[1] + dy)
                if cell in self.cells:
                    nearby_lots.update(self.cells[cell])
        
        return list(nearby_lots)
    
    def get_lots_in_area(self, min_x: float, min_y: float, 
                         max_x: float, max_y: float) -> List['Lot']:
        """
        Retorna lotes em uma área retangular.
        
        Args:
            min_x, min_y: Canto inferior esquerdo
            max_x, max_y: Canto superior direito
            
        Returns:
            Lista de lotes na área
        """
        cell_min = self._get_cell_coords(min_x, min_y)
        cell_max = self._get_cell_coords(max_x, max_y)
        
        lots = set()
        
        for cx in range(cell_min[0], cell_max[0] + 1):
            for cy in range(cell_min[1], cell_max[1] + 1):
                cell = (cx, cy)
                if cell in self.cells:
                    lots.update(self.cells[cell])
        
        return list(lots)
    
    def clear(self) -> None:
        """Limpa o índice espacial."""
        self.cells.clear()
        self.lot_to_cells.clear()
    
    def get_all_lots(self) -> List['Lot']:
        """Retorna todos os lotes no índice."""
        all_lots = set()
        for lots in self.cells.values():
            all_lots.update(lots)
        return list(all_lots)
    
    def __len__(self) -> int:
        """Retorna número de lotes no índice."""
        return len(self.lot_to_cells)
    
    def __repr__(self) -> str:
        return f"SpatialIndex(cell_size={self.cell_size}, lots={len(self)}, cells={len(self.cells)})"


# Teste do módulo
if __name__ == "__main__":
    from point import Point
    from lot import Lot
    
    # Cria índice
    index = SpatialIndex(cell_size=50.0)
    
    # Cria alguns lotes
    lot1 = Lot(0, 0, 100, 0, 100, 50, 0, 50)
    lot2 = Lot(50, 0, 150, 0, 150, 50, 50, 50)
    lot3 = Lot(200, 200, 300, 200, 300, 250, 200, 250)
    
    # Adiciona ao índice
    index.add_lot(lot1)
    index.add_lot(lot2)
    index.add_lot(lot3)
    
    print(f"Índice: {index}")
    
    # Busca lotes próximos a um ponto
    point = Point(75, 25)
    nearby = index.get_nearby_lots(point)
    print(f"\nLotes próximos a {point}: {len(nearby)}")
    
    # Remove um lote
    index.remove_lot(lot1)
    print(f"\nApós remover lot1: {index}")