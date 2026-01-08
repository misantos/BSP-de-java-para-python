"""
image_handler.py - Módulo para manipulação de imagens do BSP

Centraliza todas as funções relacionadas a:
- Criação de imagens
- Desenho de lotes, vias e quadras
- Salvamento e exportação
- Visualização de progresso

Autor: Refatoração Python
Data: 2026-01-07
"""

from PIL import Image, ImageDraw, ImageFont
from typing import List, Tuple, Optional
import os

# Tenta importar matplotlib (opcional, para visualização)
try:
    import matplotlib.pyplot as plt
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False


# ============================================================
# PALETA DE CORES
# ============================================================

COLORS = {
    # Fundo
    'background': (245, 245, 235),      # Bege claro
    
    # Lotes
    'lot_border': (34, 139, 34),        # Verde floresta
    'lot_fill': (144, 238, 144, 80),    # Verde claro translúcido
    
    # Quadrilátero inicial
    'initial_quad': (200, 100, 100),    # Vermelho suave
    
    # Vias (para uso futuro)
    'main_street': (80, 80, 80),        # Cinza escuro
    'secondary_street': (120, 120, 120), # Cinza médio
    
    # Texto
    'text': (50, 50, 50),               # Cinza escuro
    'text_light': (100, 100, 100),      # Cinza médio
}


# ============================================================
# CRIAÇÃO DE IMAGENS
# ============================================================

def create_blank_image(width: int, height: int, 
                       background_color: Tuple[int, int, int] = None) -> Image.Image:
    """
    Cria uma imagem em branco.
    
    Args:
        width: Largura da imagem em pixels
        height: Altura da imagem em pixels
        background_color: Cor de fundo RGB (opcional, usa padrão se None)
        
    Returns:
        Imagem PIL
    """
    if background_color is None:
        background_color = COLORS['background']
    
    return Image.new('RGB', (width, height), background_color)


# ============================================================
# DESENHO DE LOTES
# ============================================================

def draw_lot(draw: ImageDraw.Draw, lot, 
             border_color: Tuple[int, int, int] = None,
             border_width: int = 2,
             fill: bool = False) -> None:
    """
    Desenha um único lote na imagem.
    
    Args:
        draw: Objeto ImageDraw
        lot: Objeto Lot com os vértices
        border_color: Cor da borda (opcional)
        border_width: Espessura da borda
        fill: Se deve preencher o lote
    """
    if border_color is None:
        border_color = COLORS['lot_border']
    
    # Pontos do quadrilátero
    points = [
        (lot.top_left.x, lot.top_left.y),
        (lot.top_right.x, lot.top_right.y),
        (lot.bottom_right.x, lot.bottom_right.y),
        (lot.bottom_left.x, lot.bottom_left.y),
    ]
    
    # Preenche se solicitado
    if fill:
        draw.polygon(points, fill=COLORS['lot_fill'][:3])
    
    # Desenha borda (fecha o polígono)
    points.append(points[0])
    draw.line(points, fill=border_color, width=border_width)


def draw_lots(image: Image.Image, lots: List, 
              border_color: Tuple[int, int, int] = None,
              border_width: int = 2,
              fill: bool = False) -> Image.Image:
    """
    Desenha todos os lotes na imagem.
    
    Args:
        image: Imagem PIL onde desenhar
        lots: Lista de objetos Lot
        border_color: Cor das bordas
        border_width: Espessura das bordas
        fill: Se deve preencher os lotes
        
    Returns:
        Imagem com os lotes desenhados
    """
    draw = ImageDraw.Draw(image)
    
    for lot in lots:
        draw_lot(draw, lot, border_color, border_width, fill)
    
    return image


def draw_initial_quadrilateral(image: Image.Image, lot,
                                color: Tuple[int, int, int] = None,
                                width: int = 3) -> Image.Image:
    """
    Desenha o quadrilátero inicial (área total) na imagem.
    
    Args:
        image: Imagem PIL
        lot: Lote inicial
        color: Cor da linha
        width: Espessura da linha
        
    Returns:
        Imagem com o quadrilátero desenhado
    """
    if color is None:
        color = COLORS['initial_quad']
    
    draw = ImageDraw.Draw(image)
    points = [
        (lot.top_left.x, lot.top_left.y),
        (lot.top_right.x, lot.top_right.y),
        (lot.bottom_right.x, lot.bottom_right.y),
        (lot.bottom_left.x, lot.bottom_left.y),
        (lot.top_left.x, lot.top_left.y)  # Fecha o polígono
    ]
    draw.line(points, fill=color, width=width)
    
    return image


# ============================================================
# ANOTAÇÕES E TEXTO
# ============================================================

def draw_lot_labels(image: Image.Image, lots: List, 
                    show_id: bool = True,
                    show_area: bool = False,
                    show_dimensions: bool = False) -> Image.Image:
    """
    Adiciona labels (texto) nos lotes.
    
    Args:
        image: Imagem PIL
        lots: Lista de lotes
        show_id: Mostrar número do lote
        show_area: Mostrar área em px²
        show_dimensions: Mostrar largura x altura
        
    Returns:
        Imagem com labels
    """
    draw = ImageDraw.Draw(image)
    
    # Tenta usar uma fonte, senão usa padrão
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 10)
    except:
        font = ImageFont.load_default()
    
    for i, lot in enumerate(lots):
        # Calcula centro do lote
        center_x = (lot.top_left.x + lot.top_right.x + 
                   lot.bottom_left.x + lot.bottom_right.x) / 4
        center_y = (lot.top_left.y + lot.top_right.y + 
                   lot.bottom_left.y + lot.bottom_right.y) / 4
        
        # Monta texto
        lines = []
        if show_id:
            lines.append(f"L{i+1}")
        if show_area:
            area = lot.get_width() * lot.get_height()
            lines.append(f"{area:.0f}px²")
        if show_dimensions:
            lines.append(f"{lot.get_width():.0f}x{lot.get_height():.0f}")
        
        text = "\n".join(lines)
        
        # Desenha texto centralizado
        if text:
            # Obtém tamanho do texto
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            x = center_x - text_width / 2
            y = center_y - text_height / 2
            
            draw.text((x, y), text, fill=COLORS['text'], font=font)
    
    return image


# ============================================================
# SALVAMENTO E EXPORTAÇÃO
# ============================================================

def save_image(image: Image.Image, filepath: str, 
               create_dirs: bool = True) -> bool:
    """
    Salva a imagem em arquivo.
    
    Args:
        image: Imagem PIL
        filepath: Caminho do arquivo
        create_dirs: Se deve criar diretórios se não existirem
        
    Returns:
        True se salvou com sucesso, False caso contrário
    """
    try:
        if create_dirs:
            directory = os.path.dirname(filepath)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)
        
        image.save(filepath)
        print(f"💾 Imagem salva: {filepath}")
        return True
    except Exception as e:
        print(f"❌ Erro ao salvar imagem: {e}")
        return False


def save_result(lots: List, image: Image.Image, filepath: str,
                draw_options: dict = None) -> bool:
    """
    Salva o resultado final com os lotes desenhados.
    
    Args:
        lots: Lista de lotes
        image: Imagem base
        filepath: Caminho do arquivo
        draw_options: Opções de desenho (opcional)
            - border_width: Espessura das bordas
            - fill: Se deve preencher
            - show_labels: Se deve mostrar labels
            
    Returns:
        True se salvou com sucesso
    """
    if draw_options is None:
        draw_options = {}
    
    # Faz cópia para não modificar original
    img_copy = image.copy()
    
    # Desenha lotes
    draw_lots(
        img_copy, 
        lots,
        border_width=draw_options.get('border_width', 2),
        fill=draw_options.get('fill', False)
    )
    
    # Adiciona labels se solicitado
    if draw_options.get('show_labels', False):
        draw_lot_labels(
            img_copy, 
            lots,
            show_id=draw_options.get('show_id', True),
            show_area=draw_options.get('show_area', False),
            show_dimensions=draw_options.get('show_dimensions', False)
        )
    
    return save_image(img_copy, filepath)


# ============================================================
# VISUALIZAÇÃO
# ============================================================

def show_image(image: Image.Image, title: str = "BSP Result",
               use_matplotlib: bool = None) -> None:
    """
    Mostra a imagem na tela.
    
    Args:
        image: Imagem PIL
        title: Título da janela
        use_matplotlib: Usar matplotlib (None = auto-detectar)
    """
    if use_matplotlib is None:
        use_matplotlib = HAS_MATPLOTLIB
    
    if use_matplotlib and HAS_MATPLOTLIB:
        plt.figure(figsize=(10, 10))
        plt.imshow(image)
        plt.title(title)
        plt.axis('off')
        plt.tight_layout()
        plt.show()
    else:
        image.show(title=title)


def show_progress(lots: List, image: Image.Image, 
                  title: str = None,
                  use_matplotlib: bool = None,
                  pause: float = 0.5) -> None:
    """
    Mostra o progresso da subdivisão (para debugging/visualização).
    
    Args:
        lots: Lista de lotes atual
        image: Imagem base
        title: Título (usa contagem de lotes se None)
        pause: Tempo de pausa em segundos (só para matplotlib)
        use_matplotlib: Usar matplotlib
    """
    if title is None:
        title = f"BSP Progress - {len(lots)} lotes"
    
    if use_matplotlib is None:
        use_matplotlib = HAS_MATPLOTLIB
    
    # Cria cópia e desenha
    img_copy = image.copy()
    draw_lots(img_copy, lots)
    
    if use_matplotlib and HAS_MATPLOTLIB:
        plt.figure(figsize=(10, 10))
        plt.imshow(img_copy)
        plt.title(title)
        plt.axis('off')
        plt.tight_layout()
        plt.pause(pause)
        plt.close()
    else:
        img_copy.show(title=title)


# ============================================================
# ESTATÍSTICAS
# ============================================================

def print_statistics(lots: List, pixel_per_meter: float = 1.0) -> dict:
    """
    Calcula e imprime estatísticas dos lotes.
    
    Args:
        lots: Lista de lotes
        pixel_per_meter: Fator de conversão px → metros
        
    Returns:
        Dicionário com estatísticas
    """
    if not lots:
        print("⚠️ Nenhum lote para calcular estatísticas")
        return {}
    
    heights = [lot.get_height() for lot in lots]
    widths = [lot.get_width() for lot in lots]
    areas = [h * w for h, w in zip(heights, widths)]
    
    stats = {
        'count': len(lots),
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
    
    # Imprime
    print(f"\n📊 Estatísticas ({stats['count']} lotes)")
    print("=" * 50)
    
    unit = "px" if pixel_per_meter == 1.0 else "m"
    area_unit = "px²" if pixel_per_meter == 1.0 else "m²"
    
    print(f"\n📏 Altura:")
    print(f"   Mínima: {stats['height']['min'] / pixel_per_meter:.1f} {unit}")
    print(f"   Máxima: {stats['height']['max'] / pixel_per_meter:.1f} {unit}")
    print(f"   Média:  {stats['height']['avg'] / pixel_per_meter:.1f} {unit}")
    
    print(f"\n📐 Largura:")
    print(f"   Mínima: {stats['width']['min'] / pixel_per_meter:.1f} {unit}")
    print(f"   Máxima: {stats['width']['max'] / pixel_per_meter:.1f} {unit}")
    print(f"   Média:  {stats['width']['avg'] / pixel_per_meter:.1f} {unit}")
    
    print(f"\n📦 Área:")
    print(f"   Mínima: {stats['area']['min'] / (pixel_per_meter**2):.1f} {area_unit}")
    print(f"   Máxima: {stats['area']['max'] / (pixel_per_meter**2):.1f} {area_unit}")
    print(f"   Média:  {stats['area']['avg'] / (pixel_per_meter**2):.1f} {area_unit}")
    print(f"   Total:  {stats['area']['total'] / (pixel_per_meter**2):.1f} {area_unit}")
    
    print("=" * 50)
    
    return stats


# ============================================================
# TESTE DO MÓDULO
# ============================================================

if __name__ == "__main__":
    print("🎨 Testando image_handler.py")
    print("=" * 50)
    
    # Cria imagem de teste
    img = create_blank_image(800, 600)
    print(f"✅ Imagem criada: {img.size}")
    
    # Testa salvamento
    test_path = "/tmp/test_image_handler.png"
    if save_image(img, test_path):
        print(f"✅ Salvamento funcionando")
        os.remove(test_path)
    
    print("\n✨ Testes concluídos!")