"""
main.py - Entrada principal do algoritmo BSP

VERSÃO REFATORADA:
- Usa random nativo do Python
- Número de divisões determinístico (baseado em MIN_WIDTH/MIN_HEIGHT)
- Seed opcional
- Módulo image_handler para manipulação de imagens

Autor: Refatoração Python
Data: 2026-01-07
"""

import argparse
import os
import sys

from config_parser import BSPConfig
from lot import Lot
from lot_stack import LotStack
import image_handler as img_handler


def create_initial_lot_from_config(config: BSPConfig) -> Lot:
    """
    Cria o lote inicial a partir das configurações.
    
    Args:
        config: Objeto de configuração
        
    Returns:
        Lote inicial (quadrilátero)
    """
    cfg = config.get_all()
    
    return Lot(
        cfg['QUAD_TOP_LEFT_X'], cfg['QUAD_TOP_LEFT_Y'],
        cfg['QUAD_TOP_RIGHT_X'], cfg['QUAD_TOP_RIGHT_Y'],
        cfg['QUAD_BOTTOM_RIGHT_X'], cfg['QUAD_BOTTOM_RIGHT_Y'],
        cfg['QUAD_BOTTOM_LEFT_X'], cfg['QUAD_BOTTOM_LEFT_Y']
    )


def main():
    """Função principal."""
    # Parser de argumentos
    parser = argparse.ArgumentParser(
        description='Algoritmo BSP para subdivisão de lotes urbanos'
    )
    parser.add_argument(
        '-c', '--config',
        default='config_bsp.ini',
        help='Arquivo de configuração (padrão: config_bsp.ini)'
    )
    parser.add_argument(
        '-o', '--output',
        default='resultado_bsp.png',
        help='Arquivo de saída (padrão: resultado_bsp.png)'
    )
    parser.add_argument(
        '--show',
        action='store_true',
        help='Mostrar resultado na tela'
    )
    parser.add_argument(
        '--labels',
        action='store_true',
        help='Mostrar labels nos lotes'
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("🏘️  ALGORITMO BSP - Subdivisão de Lotes Urbanos")
    print("   Versão Refatorada - Python")
    print("=" * 60)
    
    # Carrega configurações
    config = BSPConfig(args.config)
    
    # Valida configurações
    is_valid, errors = config.validate()
    if not is_valid:
        print("\n❌ Erros na configuração:")
        for error in errors:
            print(f"   - {error}")
        sys.exit(1)
    
    # Mostra configurações
    config.print_config()
    
    # Obtém valores
    cfg = config.get_all()
    
    # Cria imagem em branco
    img = img_handler.create_blank_image(
        cfg['IMAGE_WIDTH'], 
        cfg['IMAGE_HEIGHT']
    )
    
    # Cria lote inicial
    initial_lot = create_initial_lot_from_config(config)
    
    print(f"\n📍 Lote inicial:")
    print(f"   Largura: {initial_lot.get_width():.1f} px")
    print(f"   Altura:  {initial_lot.get_height():.1f} px")
    print(f"   Área:    {initial_lot.get_area():.1f} px²")
    
    # Desenha quadrilátero inicial
    img_handler.draw_initial_quadrilateral(img, initial_lot)
    
    # Prepara configuração para LotStack
    lot_stack_config = config.to_lot_stack_config()
    
    print(f"\n🚀 Iniciando subdivisão...")
    print(f"   Objetivo: {cfg['MIN_AMOUNT_OF_LOTS']} lotes")
    print()
    
    # Executa algoritmo BSP
    lot_stack = LotStack(initial_lot, lot_stack_config)
    
    # Obtém resultado
    lots = lot_stack.get_lots()
    
    print(f"\n✅ Subdivisão concluída!")
    print(f"📦 Total de lotes: {len(lots)}")
    
    # Estatísticas
    LotStack.print_statistics()
    
    # Desenha lotes na imagem
    draw_options = {
        'border_width': 2,
        'fill': False,
        'show_labels': args.labels,
        'show_id': True,
        'show_area': False,
        'show_dimensions': False
    }
    
    img_handler.save_result(lots, img, args.output, draw_options)
    
    print(f"\n💾 Resultado salvo em: {args.output}")
    
    # Mostra na tela se solicitado
    if args.show:
        img_handler.show_image(
            img_handler.draw_lots(img.copy(), lots),
            f"BSP - {len(lots)} lotes"
        )
    
    # Verifica se todos respeitam MIN_WIDTH e MIN_HEIGHT
    violations = []
    for i, lot in enumerate(lots):
        if lot.get_width() < cfg['MIN_LOT_WIDTH']:
            violations.append(f"Lote {i+1}: largura {lot.get_width():.1f} < {cfg['MIN_LOT_WIDTH']}")
        if lot.get_height() < cfg['MIN_LOT_HEIGHT']:
            violations.append(f"Lote {i+1}: altura {lot.get_height():.1f} < {cfg['MIN_LOT_HEIGHT']}")
    
    if violations:
        print(f"\n⚠️  Violações encontradas:")
        for v in violations:
            print(f"   - {v}")
    else:
        print(f"\n✅ Todos os lotes respeitam MIN_WIDTH ({cfg['MIN_LOT_WIDTH']}px) e MIN_HEIGHT ({cfg['MIN_LOT_HEIGHT']}px)")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()