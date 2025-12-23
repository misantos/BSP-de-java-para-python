"""
Backup_LotStack - Versão alternativa/antiga do LotStack.
Subdivisão recursiva de lotes usando BSP.
"""

from collections import deque
from typing import Deque
import random
import math
from lot import Lot
from point import Point


class Backup_LotStack:
    """
    Versão backup/antiga do LotStack.
    Diferenças principais:
    - Seed fixo (123)
    - Remove lotes muito pequenos imediatamente
    - Não verifica hasAnExitToExternalArea()
    - Print de prioridade em cada partição
    """
    
    # Variáveis de classe (static)
    lots: Deque[Lot] = deque()
    MIN_LOTS: int = 0
    random_gen: random.Random = random.Random(123)  # Seed fixo
    
    # Configurações (equivalente a Main.*)
    MIN_SPLIT_X: int = 0
    MAX_SPLIT_X: int = 0
    MIN_SPLIT_Y: int = 0
    MAX_SPLIT_Y: int = 0
    MIN_HEIGHT_LOT: int = 0
    MIN_WIDTH_LOT: int = 0
    
    # Callback para desenhar (opcional)
    draw_callback = None
    img = None
    
    def __init__(self, initial_lot: Lot, config: dict):
        """
        Inicializa o Backup_LotStack e começa a subdivisão.
        
        Args:
            initial_lot: Lote inicial
            config: Dicionário com configurações
        """
        # Limpa lotes anteriores
        Backup_LotStack.lots.clear()
        
        # Configura variáveis estáticas
        Backup_LotStack.MIN_LOTS = config['MIN_LOTS']
        # Seed fixo em 123 (não usa config)
        Backup_LotStack.random_gen = random.Random(123)
        
        Backup_LotStack.MIN_SPLIT_X = config['MIN_SPLIT_X']
        Backup_LotStack.MAX_SPLIT_X = config['MAX_SPLIT_X']
        Backup_LotStack.MIN_SPLIT_Y = config['MIN_SPLIT_Y']
        Backup_LotStack.MAX_SPLIT_Y = config['MAX_SPLIT_Y']
        Backup_LotStack.MIN_HEIGHT_LOT = config['MIN_HEIGHT_LOT']
        Backup_LotStack.MIN_WIDTH_LOT = config['MIN_WIDTH_LOT']
        
        Backup_LotStack.draw_callback = config.get('draw_callback')
        Backup_LotStack.img = config.get('img')
        
        # Inicia subdivisão
        Backup_LotStack.partite_lot(initial_lot)
        
        # Continua subdividindo até atingir MIN_LOTS
        while len(Backup_LotStack.lots) < Backup_LotStack.MIN_LOTS:
            min_priority = float('inf')  # Integer.MAX_VALUE
            
            print(min_priority)
            
            # Desenha progresso
            if Backup_LotStack.draw_callback and Backup_LotStack.img:
                Backup_LotStack.draw_callback(list(Backup_LotStack.lots), Backup_LotStack.img.copy())
            
            # Calcula prioridade mínima
            for lot in Backup_LotStack.lots:
                if lot.priority < min_priority:
                    min_priority = lot.priority
            
            # Particiona apenas lotes com prioridade mínima
            for lot in list(Backup_LotStack.lots):
                if lot.priority > min_priority:
                    continue
                Backup_LotStack.partite_lot(lot)
    
    @staticmethod
    def partite_lot(lot_to_partition: Lot) -> None:
        """
        Função recursiva para separar os lotes.
        Versão backup - comportamento diferente do LotStack normal.
        
        Args:
            lot_to_partition: Lote a ser subdividido
        """
        print(f"Prioridade: {lot_to_partition.priority}")
        
        # Breaks if reached the min number of lots
        if len(Backup_LotStack.lots) >= Backup_LotStack.MIN_LOTS:
            return
        
        # If very small - REMOVE o lote e retorna
        if (lot_to_partition.get_height() < Backup_LotStack.MIN_HEIGHT_LOT or 
            lot_to_partition.get_width() < Backup_LotStack.MIN_WIDTH_LOT):
            try:
                Backup_LotStack.lots.remove(lot_to_partition)
            except ValueError:
                pass
            return
        
        # Horizontal or vertical division
        if Backup_LotStack.random_gen.random() < 0.5:  # horizontal
            # right
            dx_right = lot_to_partition.bottom_right.x - lot_to_partition.top_right.x
            dy_right = lot_to_partition.bottom_right.y - lot_to_partition.top_right.y
            
            # left
            dx_left = lot_to_partition.bottom_left.x - lot_to_partition.top_left.x
            dy_left = lot_to_partition.bottom_left.y - lot_to_partition.top_left.y
            
            # New divisions of the edges
            anchor_points = int(math.ceil(
                Backup_LotStack.MIN_SPLIT_X + 
                Backup_LotStack.random_gen.randint(0, int(Backup_LotStack.MAX_SPLIT_X - Backup_LotStack.MIN_SPLIT_X) - 1)
            ))
            
            for k in range(1, anchor_points + 1):
                ini_left_x = lot_to_partition.top_left.x
                ini_left_y = lot_to_partition.top_left.y
                
                ini_right_x = lot_to_partition.top_right.x
                ini_right_y = lot_to_partition.top_right.y
                
                # IMPORTANTE: Coordenadas diferentes do LotStack normal
                new_lot = Lot(
                    ini_left_x, ini_left_y,
                    ini_right_x, ini_right_y,
                    ini_right_x + dx_right * k / anchor_points,
                    ini_right_y + dy_right * k / anchor_points,
                    ini_left_x + dx_left * k / anchor_points,
                    ini_left_y + dy_left * k / anchor_points
                )
                
                new_lot.priority = lot_to_partition.priority + 1
                
                Backup_LotStack.lots.append(new_lot)
                # partiteLot(newLot) está comentado no Java
        
        else:  # vertical
            # top
            dx_top = lot_to_partition.top_right.x - lot_to_partition.top_left.x
            dy_top = lot_to_partition.top_right.y - lot_to_partition.top_left.y
            
            # bottom
            dx_bottom = lot_to_partition.bottom_right.x - lot_to_partition.bottom_left.x
            dy_bottom = lot_to_partition.bottom_right.y - lot_to_partition.bottom_left.y
            
            # New divisions of the edges
            anchor_points = int(math.ceil(
                Backup_LotStack.MIN_SPLIT_Y + 
                Backup_LotStack.random_gen.randint(0, int(Backup_LotStack.MAX_SPLIT_Y - Backup_LotStack.MIN_SPLIT_Y) - 1)
            ))
            
            for k in range(1, anchor_points + 1):
                ini_top_left_x = lot_to_partition.top_left.x
                ini_top_left_y = lot_to_partition.top_left.y
                
                ini_bottom_left_x = lot_to_partition.bottom_left.x
                ini_bottom_left_y = lot_to_partition.bottom_left.y
                
                # IMPORTANTE: Coordenadas diferentes do LotStack normal
                new_lot = Lot(
                    ini_top_left_x, ini_top_left_y,
                    ini_top_left_x + dx_top * k / anchor_points,
                    ini_top_left_y + dy_top * k / anchor_points,
                    ini_bottom_left_x + dx_bottom * k / anchor_points,
                    ini_bottom_left_y + dy_bottom * k / anchor_points,
                    ini_bottom_left_x, ini_bottom_left_y
                )
                
                new_lot.priority = lot_to_partition.priority + 1
                
                Backup_LotStack.lots.append(new_lot)
                # partiteLot(newLot) está comentado no Java
        
        # Remove o lote pai
        try:
            Backup_LotStack.lots.remove(lot_to_partition)
        except ValueError:
            pass
    
    def get_lots(self) -> list[Lot]:
        """
        Retorna a lista de todos os lotes.
        
        Returns:
            Lista de lotes
        """
        return list(Backup_LotStack.lots)