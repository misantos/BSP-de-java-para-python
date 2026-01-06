"""
Main - Programa principal para subdivisão de lotes usando BSP.
Binary Space Partitioning para planejamento urbano.
Lê configurações de arquivo config_bsp.ini (compatível com versão Java).
"""

import argparse
from PIL import Image, ImageDraw
import sys
import time
from lot import Lot
from lot_stack import LotStack
from point import Point
from config_parser import BSPConfig, create_default_config

# Tenta importar matplotlib para visualização mais estável
try:
    import matplotlib.pyplot as plt
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False


def draw_lots(lots: list[Lot], image: Image.Image, 
              color: tuple = (0, 255, 0), width: int = 2) -> Image.Image:
    """
    Desenha todos os lotes na imagem.
    
    Args:
        lots: Lista de lotes a desenhar
        image: Imagem PIL onde desenhar
        color: Cor das linhas (R, G, B)
        width: Espessura das linhas
        
    Returns:
        Imagem com os lotes desenhados
    """
    draw = ImageDraw.Draw(image)
    
    for lot in lots:
        # Desenha o quadrilátero conectando os 4 vértices
        points = [
            (lot.top_left.x, lot.top_left.y),
            (lot.top_right.x, lot.top_right.y),
            (lot.bottom_right.x, lot.bottom_right.y),
            (lot.bottom_left.x, lot.bottom_left.y),
            (lot.top_left.x, lot.top_left.y)  # Fecha o polígono
        ]
        draw.line(points, fill=color, width=width)
    
    return image


def show_and_save_lots(lots: list[Lot], img: Image.Image, 
                       filename: str = None, show: bool = True, use_matplotlib: bool = False):
    """
    Desenha, mostra e/ou salva a imagem com os lotes.
    IMPORTANTE: Mostra a imagem em uma janela (como Java showImage()).
    
    Args:
        lots: Lista de lotes
        img: Imagem base
        filename: Nome do arquivo para salvar (opcional)
        show: Se deve mostrar a imagem (padrão: True)
        use_matplotlib: Se deve usar matplotlib ao invés do visualizador padrão
    """
    img_copy = img.copy()
    img_with_lots = draw_lots(lots, img_copy)
    
    if filename:
        img_with_lots.save(filename)
        print(f"  📄 Imagem salva: {filename}")
    
    if show:
        if use_matplotlib and HAS_MATPLOTLIB:
            # Usa matplotlib - mais estável e controla melhor as janelas
            plt.figure(figsize=(10, 10))
            plt.imshow(img_with_lots)
            plt.title(f'BSP Progress - {len(lots)} lotes')
            plt.axis('off')
            plt.tight_layout()
            plt.pause(0.5)  # Mostra por 0.5 segundos
            plt.close()
        else:
            # Usa visualizador padrão do sistema
            # Salva temporariamente para evitar problemas de memória
            temp_filename = f"_temp_progress_{len(lots)}.png"
            img_with_lots.save(temp_filename)
            img_with_lots.show(title=f"BSP - {len(lots)} lotes")
            time.sleep(0.3)  # Pequeno delay


def create_initial_lot_from_config(config: BSPConfig) -> Lot:
    """
    Cria o lote inicial baseado nas configurações.
    
    Args:
        config: Objeto de configuração BSP
        
    Returns:
        Lote inicial
    """
    cfg = config.get_all()
    return Lot(
        cfg['QUAD_TOP_LEFT_X'], cfg['QUAD_TOP_LEFT_Y'],
        cfg['QUAD_TOP_RIGHT_X'], cfg['QUAD_TOP_RIGHT_Y'],
        cfg['QUAD_BOTTOM_RIGHT_X'], cfg['QUAD_BOTTOM_RIGHT_Y'],
        cfg['QUAD_BOTTOM_LEFT_X'], cfg['QUAD_BOTTOM_LEFT_Y']
    )


def create_blank_image(width: int, height: int, 
                      background_color: tuple = (240, 240, 240)) -> Image.Image:
    """
    Cria uma imagem em branco.
    
    Args:
        width: Largura da imagem
        height: Altura da imagem
        background_color: Cor de fundo (R, G, B)
        
    Returns:
        Imagem PIL
    """
    return Image.new('RGB', (width, height), background_color)


def draw_initial_quad(img: Image.Image, lot: Lot, 
                     color: tuple = (200, 100, 100), width: int = 3):
    """
    Desenha o quadrilátero inicial na imagem.
    
    Args:
        img: Imagem onde desenhar
        lot: Lote inicial
        color: Cor da linha
        width: Espessura da linha
    """
    draw = ImageDraw.Draw(img)
    points = [
        (lot.top_left.x, lot.top_left.y),
        (lot.top_right.x, lot.top_right.y),
        (lot.bottom_right.x, lot.bottom_right.y),
        (lot.bottom_left.x, lot.bottom_left.y),
        (lot.top_left.x, lot.top_left.y)
    ]
    draw.line(points, fill=color, width=width)


def main():
    """Função principal."""
    parser = argparse.ArgumentParser(
        description='Subdivisão de lotes usando BSP (Binary Space Partitioning)\n'
                    'Lê configurações de config_bsp.ini',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('--config', type=str, default='config_bsp.ini',
                       help='Caminho para arquivo de configuração (padrão: config_bsp.ini)')
    parser.add_argument('--create-config', action='store_true',
                       help='Cria arquivo de configuração padrão e sai')
    parser.add_argument('--output', type=str, default='resultado_bsp.png',
                       help='Nome do arquivo de saída (padrão: resultado_bsp.png)')
    parser.add_argument('--no-display', action='store_true',
                       help='Não mostrar janelas durante o processo (apenas salvar no final)')
    parser.add_argument('--save-progress', action='store_true',
                       help='Salvar imagens de progresso em arquivos')
    parser.add_argument('--use-matplotlib', action='store_true',
                       help='Usar matplotlib para visualização (mais estável em Linux)')
    
    args = parser.parse_args()
    
    # Se pediu para criar config, cria e sai
    if args.create_config:
        create_default_config(args.config)
        return
    
    # Carrega configurações
    try:
        print(f"📖 Carregando configurações: {args.config}")
        config = BSPConfig(args.config)
    except FileNotFoundError:
        print(f"❌ Arquivo não encontrado: {args.config}")
        print(f"\nPara criar um arquivo de configuração padrão, execute:")
        print(f"  python main.py --create-config")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Erro ao ler configuração: {e}")
        sys.exit(1)
    
    # Valida configurações
    valid, errors = config.validate()
    if not valid:
        print("❌ Erros nas configurações:")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)
    
    # Mostra configurações
    config.print_config()
    
    # Obtém configurações
    cfg = config.get_all()
    
    # Cria imagem em branco
    print(f"🎨 Criando imagem {cfg['IMAGE_WIDTH']}x{cfg['IMAGE_HEIGHT']}...")
    img = create_blank_image(cfg['IMAGE_WIDTH'], cfg['IMAGE_HEIGHT'])
    
    # Cria lote inicial
    print(f"🔷 Criando quadrilátero inicial...")
    initial_lot = create_initial_lot_from_config(config)
    
    # Desenha quadrilátero inicial na imagem
    draw_initial_quad(img, initial_lot)
    
    # Prepara configurações para LotStack
    lot_stack_config = {
        'MIN_LOTS': cfg['MIN_AMOUNT_OF_LOTS'],
        'MIN_HEIGHT_LOT': cfg['MIN_LOT_HEIGHT'],
        'MIN_WIDTH_LOT': cfg['MIN_LOT_WIDTH'],
        'MAX_HEIGHT_LOT': cfg['MAX_LOT_HEIGHT'],
        'MAX_WIDTH_LOT': cfg['MAX_LOT_WIDTH'],
        'MIN_SPLIT_X': cfg['MIN_SPLITS_IN_X_AXIS'],
        'MAX_SPLIT_X': cfg['MAX_SPLITS_IN_X_AXIS'],
        'MIN_SPLIT_Y': cfg['MIN_SPLITS_IN_Y_AXIS'],
        'MAX_SPLIT_Y': cfg['MAX_SPLITS_IN_Y_AXIS'],
        'SEED': cfg['SEED'],
        'img': img
    }
    
    # Adiciona callback para mostrar progresso (como no Java)
    if not args.no_display:
        # Mostra janelas durante o processo (igual ao Java)
        lot_stack_config['draw_callback'] = lambda lots, image: show_and_save_lots(
            lots, image, 
            f"progresso_{len(lots)}_lotes.png" if args.save_progress else None,
            show=True,
            use_matplotlib=args.use_matplotlib
        )
    elif args.save_progress:
        # Apenas salva, sem mostrar
        lot_stack_config['draw_callback'] = lambda lots, image: show_and_save_lots(
            lots, image, 
            f"progresso_{len(lots)}_lotes.png",
            show=False,
            use_matplotlib=False
        )
    
    # Executa subdivisão BSP
    print(f"\n🔀 Iniciando subdivisão BSP...")
    print("=" * 60)
    
    try:
        lot_stack = LotStack(initial_lot, lot_stack_config)
        print("=" * 60)
    except Exception as e:
        print(f"\n❌ Erro durante subdivisão: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # Obtém resultados
    final_lots = lot_stack.get_lots()
    print(f"\n✅ Subdivisão concluída!")
    print(f"📦 Total de lotes criados: {len(final_lots)}")
    
    # Estatísticas
    if len(final_lots) > 0:
        heights = [lot.get_height() for lot in final_lots]
        widths = [lot.get_width() for lot in final_lots]
        areas = [h * w for h, w in zip(heights, widths)]
        
        print(f"\n📊 Estatísticas:")
        print(f"  Altura:")
        print(f"    - Mínima: {min(heights):.1f}px")
        print(f"    - Máxima: {max(heights):.1f}px")
        print(f"    - Média: {sum(heights)/len(heights):.1f}px")
        print(f"  Largura:")
        print(f"    - Mínima: {min(widths):.1f}px")
        print(f"    - Máxima: {max(widths):.1f}px")
        print(f"    - Média: {sum(widths)/len(widths):.1f}px")
        print(f"  Área:")
        print(f"    - Mínima: {min(areas):.1f}px²")
        print(f"    - Máxima: {max(areas):.1f}px²")
        print(f"    - Média: {sum(areas)/len(areas):.1f}px²")
    
    # Desenha e salva resultado final
    print(f"\n💾 Salvando resultado final...")
    show_and_save_lots(final_lots, img, args.output, 
                      show=not args.no_display,
                      use_matplotlib=args.use_matplotlib)
    
    print("\n✨ Processo concluído com sucesso!")
    print(f"\n💡 Dica: Para gerar resultados diferentes, altere o SEED no arquivo {args.config}")


if __name__ == "__main__":
    main()