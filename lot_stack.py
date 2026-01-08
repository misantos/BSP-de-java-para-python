"""
lot_stack.py - Algoritmo BSP para subdivisão de lotes urbanos

VERSÃO REFATORADA:
- Usa random nativo do Python (não mais JavaRandom)
- Número de divisões calculado por MIN_WIDTH/MIN_HEIGHT (determinístico)
- Direção de corte ainda aleatória (50%/50%)
- Seed opcional
- Lotes respeitam MIN_WIDTH e MIN_HEIGHT

Autor: Refatoração Python
Data: 2026-01-07
"""

import random
import math
from collections import deque
from typing import List, Deque, Optional, Dict, Any

from point import Point
from lot import Lot
from spatial_index import SpatialIndex


class LotStack:
    """
    Gerencia a subdivisão de lotes usando BSP (Binary Space Partitioning).
    
    Nova lógica de subdivisão:
    - Direção: aleatória (50% horizontal, 50% vertical)
    - Número de divisões: calculado para respeitar MIN_WIDTH/MIN_HEIGHT
    - Limitado pelo MAX_SPLIT_X/MAX_SPLIT_Y
    """
    
    # Variáveis de classe (estado compartilhado)
    lots: Deque[Lot] = deque()
    spatial_index: Optional[SpatialIndex] = None
    
    # Configurações
    MIN_LOTS: int = 45
    MIN_HEIGHT_LOT: float = 155.0
    MIN_WIDTH_LOT: float = 125.0
    MAX_HEIGHT_LOT: float = 1000.0
    MAX_WIDTH_LOT: float = 1000.0
    MIN_SPLIT_X: int = 1
    MAX_SPLIT_X: int = 5
    MIN_SPLIT_Y: int = 1
    MAX_SPLIT_Y: int = 5
    
    # Gerador aleatório
    _random: random.Random = None
    
    def __init__(self, initial_lot: Lot, config: Dict[str, Any]):
        """
        Inicializa o algoritmo BSP e executa a subdivisão.
        
        Args:
            initial_lot: Lote inicial (área total)
            config: Dicionário de configuração:
                - MIN_LOTS: Número mínimo de lotes
                - MIN_HEIGHT_LOT: Altura mínima do lote
                - MIN_WIDTH_LOT: Largura mínima do lote
                - MAX_HEIGHT_LOT: Altura máxima do lote
                - MAX_WIDTH_LOT: Largura máxima do lote
                - MIN_SPLIT_X: Mínimo de divisões horizontais
                - MAX_SPLIT_X: Máximo de divisões horizontais
                - MIN_SPLIT_Y: Mínimo de divisões verticais
                - MAX_SPLIT_Y: Máximo de divisões verticais
                - SEED: Seed para gerador aleatório (opcional)
        """
        # Limpa estado anterior
        LotStack.lots.clear()
        
        # Carrega configurações
        LotStack.MIN_LOTS = config.get('MIN_LOTS', 45)
        LotStack.MIN_HEIGHT_LOT = config.get('MIN_HEIGHT_LOT', 155.0)
        LotStack.MIN_WIDTH_LOT = config.get('MIN_WIDTH_LOT', 125.0)
        LotStack.MAX_HEIGHT_LOT = config.get('MAX_HEIGHT_LOT', 1000.0)
        LotStack.MAX_WIDTH_LOT = config.get('MAX_WIDTH_LOT', 1000.0)
        LotStack.MIN_SPLIT_X = config.get('MIN_SPLIT_X', 1)
        LotStack.MAX_SPLIT_X = config.get('MAX_SPLIT_X', 5)
        LotStack.MIN_SPLIT_Y = config.get('MIN_SPLIT_Y', 1)
        LotStack.MAX_SPLIT_Y = config.get('MAX_SPLIT_Y', 5)
        
        # Configura gerador aleatório
        seed = config.get('SEED', None)
        if seed is not None:
            LotStack._random = random.Random(seed)
            print(f"🎲 Usando SEED: {seed}")
        else:
            LotStack._random = random.Random()
            print("🎲 Usando seed aleatória")
        
        # Inicializa índice espacial
        LotStack.spatial_index = SpatialIndex(cell_size=100.0)
        LotStack.spatial_index.add_lot(initial_lot)
        
        print(f"📊 Configuração:")
        print(f"   MIN_LOTS: {LotStack.MIN_LOTS}")
        print(f"   MIN_WIDTH: {LotStack.MIN_WIDTH_LOT} px")
        print(f"   MIN_HEIGHT: {LotStack.MIN_HEIGHT_LOT} px")
        print(f"   MAX_SPLIT_X: {LotStack.MAX_SPLIT_X}")
        print(f"   MAX_SPLIT_Y: {LotStack.MAX_SPLIT_Y}")
        
        # Executa primeira subdivisão
        LotStack._partite_lot(initial_lot)
        
        # Loop principal
        self._main_loop()
    
    def _main_loop(self) -> None:
        """Loop principal de subdivisão."""
        max_attempts = LotStack.MIN_LOTS * 20
        attempts = 0
        stagnation_counter = 0
        max_stagnation = 15
        last_lot_count = 0
        
        while len(LotStack.lots) < LotStack.MIN_LOTS:
            current_count = len(LotStack.lots)
            
            # Debug
            if current_count != last_lot_count:
                print(f"   Lotes: {current_count}")
            
            # Verifica limite de tentativas
            attempts += 1
            if attempts >= max_attempts:
                print(f"⚠️  Limite de tentativas atingido ({max_attempts})")
                break
            
            # Detecta estagnação
            if current_count == last_lot_count:
                stagnation_counter += 1
                if stagnation_counter >= max_stagnation:
                    print(f"⚠️  Subdivisão estagnada (sem progresso em {max_stagnation} tentativas)")
                    break
            else:
                stagnation_counter = 0
                last_lot_count = current_count
            
            # Seleciona e subdivide lotes
            self._select_and_subdivide()
    
    def _select_and_subdivide(self) -> None:
        """Seleciona lotes para subdividir baseado em critérios."""
        if not LotStack.lots:
            return
        
        # Encontra menor prioridade (lotes mais "antigos"/maiores)
        min_priority = min(lot.priority for lot in LotStack.lots)
        
        # Calcula área média
        areas = [lot.get_area() for lot in LotStack.lots]
        avg_area = sum(areas) / len(areas)
        large_area_threshold = avg_area * 3.0
        
        # Seleciona lotes para subdividir (cópia para evitar modificação durante iteração)
        for lot in list(LotStack.lots):
            lot_area = lot.get_area()
            
            # Critérios para subdividir
            should_subdivide = (
                lot.priority <= min_priority or
                lot.get_width() >= LotStack.MAX_WIDTH_LOT or
                lot.get_height() >= LotStack.MAX_HEIGHT_LOT or
                lot_area > large_area_threshold
            )
            
            if should_subdivide:
                LotStack._partite_lot(lot)
                
                # Verifica se atingiu objetivo
                if len(LotStack.lots) >= LotStack.MIN_LOTS:
                    return
    
    @staticmethod
    def _calculate_max_divisions(dimension: float, min_size: float, max_split: int) -> int:
        """
        Calcula o número máximo de divisões respeitando tamanho mínimo.
        
        LÓGICA DETERMINÍSTICA:
        - Calcula quantos lotes cabem respeitando MIN_WIDTH/MIN_HEIGHT
        - Limita pelo MAX_SPLIT
        
        Args:
            dimension: Largura ou altura do lote
            min_size: Tamanho mínimo permitido (MIN_WIDTH ou MIN_HEIGHT)
            max_split: Número máximo de divisões permitido
            
        Returns:
            Número de divisões a fazer
        """
        # Quantos lotes cabem respeitando o tamanho mínimo?
        max_possible = int(dimension / min_size)
        
        # Garante pelo menos 1 divisão
        max_possible = max(1, max_possible)
        
        # Limita pelo MAX_SPLIT
        divisions = min(max_possible, max_split)
        
        return divisions
    
    @staticmethod
    def _partite_lot(lot_to_partition: Lot) -> None:
        """
        Subdivide um lote em partes menores.
        
        LÓGICA:
        1. Direção: aleatória (50% horizontal, 50% vertical)
        2. Número de divisões: calculado por MIN_WIDTH/MIN_HEIGHT
        3. Cria lotes por interpolação
        4. Valida tamanho mínimo e saída
        5. Se todos válidos: aceita subdivisão
        """
        # Para se já atingiu objetivo
        if len(LotStack.lots) >= LotStack.MIN_LOTS:
            return
        
        # Lista temporária para novos lotes
        potential_lots = []
        
        # Escolhe direção ALEATÓRIA (50%/50%)
        is_horizontal = LotStack._random.random() < 0.5
        
        if is_horizontal:
            # ═══ SUBDIVISÃO HORIZONTAL (cortes verticais) ═══
            # Divide ao longo do eixo X
            
            # Calcula número de divisões (DETERMINÍSTICO)
            lot_width = lot_to_partition.get_width()
            num_divisions = LotStack._calculate_max_divisions(
                lot_width, 
                LotStack.MIN_WIDTH_LOT,
                LotStack.MAX_SPLIT_X
            )
            
            if num_divisions < 1:
                return
            
            # Vetores para interpolação (esquerda → direita)
            dx_top = lot_to_partition.top_right.x - lot_to_partition.top_left.x
            dy_top = lot_to_partition.top_right.y - lot_to_partition.top_left.y
            dx_bottom = lot_to_partition.bottom_right.x - lot_to_partition.bottom_left.x
            dy_bottom = lot_to_partition.bottom_right.y - lot_to_partition.bottom_left.y
            
            # Cria lotes por interpolação
            for k in range(1, num_divisions + 1):
                t_start = (k - 1) / num_divisions
                t_end = k / num_divisions
                
                new_lot = Lot(
                    # Top left
                    lot_to_partition.top_left.x + dx_top * t_start,
                    lot_to_partition.top_left.y + dy_top * t_start,
                    # Top right
                    lot_to_partition.top_left.x + dx_top * t_end,
                    lot_to_partition.top_left.y + dy_top * t_end,
                    # Bottom right
                    lot_to_partition.bottom_left.x + dx_bottom * t_end,
                    lot_to_partition.bottom_left.y + dy_bottom * t_end,
                    # Bottom left
                    lot_to_partition.bottom_left.x + dx_bottom * t_start,
                    lot_to_partition.bottom_left.y + dy_bottom * t_start
                )
                new_lot.priority = lot_to_partition.priority + 1
                potential_lots.append(new_lot)
        
        else:
            # ═══ SUBDIVISÃO VERTICAL (cortes horizontais) ═══
            # Divide ao longo do eixo Y
            
            # Calcula número de divisões (DETERMINÍSTICO)
            lot_height = lot_to_partition.get_height()
            num_divisions = LotStack._calculate_max_divisions(
                lot_height,
                LotStack.MIN_HEIGHT_LOT,
                LotStack.MAX_SPLIT_Y
            )
            
            if num_divisions < 1:
                return
            
            # Vetores para interpolação (topo → base)
            dx_left = lot_to_partition.bottom_left.x - lot_to_partition.top_left.x
            dy_left = lot_to_partition.bottom_left.y - lot_to_partition.top_left.y
            dx_right = lot_to_partition.bottom_right.x - lot_to_partition.top_right.x
            dy_right = lot_to_partition.bottom_right.y - lot_to_partition.top_right.y
            
            # Cria lotes por interpolação
            for k in range(1, num_divisions + 1):
                t_start = (k - 1) / num_divisions
                t_end = k / num_divisions
                
                new_lot = Lot(
                    # Top left
                    lot_to_partition.top_left.x + dx_left * t_start,
                    lot_to_partition.top_left.y + dy_left * t_start,
                    # Top right
                    lot_to_partition.top_right.x + dx_right * t_start,
                    lot_to_partition.top_right.y + dy_right * t_start,
                    # Bottom right
                    lot_to_partition.top_right.x + dx_right * t_end,
                    lot_to_partition.top_right.y + dy_right * t_end,
                    # Bottom left
                    lot_to_partition.top_left.x + dx_left * t_end,
                    lot_to_partition.top_left.y + dy_left * t_end
                )
                new_lot.priority = lot_to_partition.priority + 1
                potential_lots.append(new_lot)
        
        # ═══ VALIDAÇÃO DOS LOTES ═══
        for lot in potential_lots:
            # Validação 1: Tamanho mínimo
            if lot.get_width() < LotStack.MIN_WIDTH_LOT:
                # Lote muito estreito → CANCELA SUBDIVISÃO
                return
            
            if lot.get_height() < LotStack.MIN_HEIGHT_LOT:
                # Lote muito baixo → CANCELA SUBDIVISÃO
                return
            
            # Validação 2: Saída para área externa
            if not lot.has_an_exit_to_external_area(LotStack.spatial_index):
                # Lote cercado → CANCELA SUBDIVISÃO
                return
        
        # ═══ SUBDIVISÃO ACEITA ═══
        
        # Remove lote pai do índice espacial
        if LotStack.spatial_index:
            LotStack.spatial_index.remove_lot(lot_to_partition)
        
        # Remove lote pai da lista
        try:
            LotStack.lots.remove(lot_to_partition)
        except ValueError:
            pass  # Já foi removido (primeira subdivisão)
        
        # Adiciona lotes filhos
        LotStack.lots.extend(potential_lots)
        
        # Adiciona filhos ao índice espacial
        if LotStack.spatial_index:
            for lot in potential_lots:
                LotStack.spatial_index.add_lot(lot)
    
    def get_lots(self) -> List[Lot]:
        """Retorna lista de todos os lotes."""
        return list(LotStack.lots)
    
    @classmethod
    def get_statistics(cls) -> Dict[str, Any]:
        """Retorna estatísticas dos lotes."""
        if not cls.lots:
            return {}
        
        heights = [lot.get_height() for lot in cls.lots]
        widths = [lot.get_width() for lot in cls.lots]
        areas = [lot.get_area() for lot in cls.lots]
        
        return {
            'count': len(cls.lots),
            'height': {
                'min': min(heights),
                'max': max(heights),
                'avg': sum(heights) / len(heights)
            },
            'width': {
                'min': min(widths),
                'max': max(widths),
                'avg': sum(widths) / len(widths)
            },
            'area': {
                'min': min(areas),
                'max': max(areas),
                'avg': sum(areas) / len(areas),
                'total': sum(areas)
            }
        }
    
    @classmethod
    def print_statistics(cls) -> None:
        """Imprime estatísticas dos lotes."""
        stats = cls.get_statistics()
        
        if not stats:
            print("⚠️  Nenhum lote para calcular estatísticas")
            return
        
        print(f"\n📊 Estatísticas ({stats['count']} lotes)")
        print("=" * 50)
        
        print(f"\n📏 Altura:")
        print(f"   Mínima: {stats['height']['min']:.1f} px")
        print(f"   Máxima: {stats['height']['max']:.1f} px")
        print(f"   Média:  {stats['height']['avg']:.1f} px")
        
        print(f"\n📐 Largura:")
        print(f"   Mínima: {stats['width']['min']:.1f} px")
        print(f"   Máxima: {stats['width']['max']:.1f} px")
        print(f"   Média:  {stats['width']['avg']:.1f} px")
        
        print(f"\n📦 Área:")
        print(f"   Mínima: {stats['area']['min']:.1f} px²")
        print(f"   Máxima: {stats['area']['max']:.1f} px²")
        print(f"   Média:  {stats['area']['avg']:.1f} px²")
        print(f"   Total:  {stats['area']['total']:.1f} px²")
        
        print("=" * 50)


# Teste do módulo
if __name__ == "__main__":
    print("🧪 Testando LotStack refatorado")
    print("=" * 50)
    
    # Cria lote inicial
    initial_lot = Lot(
        100, 200,    # Top left
        600, 200,    # Top right
        650, 1200,   # Bottom right
        150, 1100    # Bottom left
    )
    
    print(f"\n📍 Lote inicial:")
    print(f"   Largura: {initial_lot.get_width():.1f} px")
    print(f"   Altura: {initial_lot.get_height():.1f} px")
    print(f"   Área: {initial_lot.get_area():.1f} px²")
    
    # Configuração
    config = {
        'MIN_LOTS': 20,
        'MIN_HEIGHT_LOT': 155,
        'MIN_WIDTH_LOT': 125,
        'MAX_HEIGHT_LOT': 500,
        'MAX_WIDTH_LOT': 500,
        'MIN_SPLIT_X': 1,
        'MAX_SPLIT_X': 4,
        'MIN_SPLIT_Y': 1,
        'MAX_SPLIT_Y': 4,
        'SEED': 42  # Seed opcional
    }
    
    print(f"\n🚀 Iniciando subdivisão (MIN_LOTS={config['MIN_LOTS']})...")
    print()
    
    # Executa BSP
    lot_stack = LotStack(initial_lot, config)
    
    # Resultado
    lots = lot_stack.get_lots()
    
    print(f"\n✅ Subdivisão concluída!")
    print(f"📦 Total de lotes: {len(lots)}")
    
    # Estatísticas
    LotStack.print_statistics()
    
    # Verifica se todos respeitam MIN_WIDTH e MIN_HEIGHT
    all_valid = True
    for i, lot in enumerate(lots):
        if lot.get_width() < config['MIN_WIDTH_LOT']:
            print(f"❌ Lote {i+1}: largura {lot.get_width():.1f} < {config['MIN_WIDTH_LOT']}")
            all_valid = False
        if lot.get_height() < config['MIN_HEIGHT_LOT']:
            print(f"❌ Lote {i+1}: altura {lot.get_height():.1f} < {config['MIN_HEIGHT_LOT']}")
            all_valid = False
    
    if all_valid:
        print(f"\n✅ Todos os lotes respeitam MIN_WIDTH ({config['MIN_WIDTH_LOT']}px) e MIN_HEIGHT ({config['MIN_HEIGHT_LOT']}px)")