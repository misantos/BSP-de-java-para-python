"""
Config Parser - Lê arquivos de configuração .ini para o sistema BSP.
"""

import configparser
from typing import Dict, Any
import io


class BSPConfig:
    """Gerencia a leitura e validação de configurações do BSP."""
    
    def __init__(self, config_file: str = "config_bsp.ini"):
        """
        Inicializa o leitor de configurações.
        
        Args:
            config_file: Caminho para o arquivo .ini
        """
        self.config_file = config_file
        self.config = self._read_config()
    
    def _read_config(self) -> Dict[str, Any]:
        """
        Lê o arquivo de configuração .ini.
        Aceita arquivos com ou sem seção [DEFAULT].
        
        Returns:
            Dicionário com todas as configurações
        """
        parser = configparser.ConfigParser()
        
        # Lê o arquivo e adiciona seção [DEFAULT] se não tiver
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Se não começa com [, adiciona seção DEFAULT
            if not content.strip().startswith('['):
                content = '[DEFAULT]\n' + content
            
            parser.read_string(content)
        except FileNotFoundError:
            raise FileNotFoundError(f"Arquivo não encontrado: {self.config_file}")
        
        # Pega a seção (DEFAULT ou primeira disponível)
        if parser.has_section('DEFAULT') or parser.defaults():
            section = parser.defaults()
        else:
            section = parser[parser.sections()[0]] if parser.sections() else {}
        
        config = {
            # Dimensões da imagem
            'IMAGE_WIDTH': int(section.get('IMAGE_WIDTH', 1300)),
            'IMAGE_HEIGHT': int(section.get('IMAGE_HEIGHT', 1300)),
            
            # Splits (subdivisões)
            'MIN_SPLITS_IN_X_AXIS': int(section.get('MIN_SPLITS_IN_X_AXIS', 1)),
            'MIN_SPLITS_IN_Y_AXIS': int(section.get('MIN_SPLITS_IN_Y_AXIS', 1)),
            'MAX_SPLITS_IN_X_AXIS': int(section.get('MAX_SPLITS_IN_X_AXIS', 5)),
            'MAX_SPLITS_IN_Y_AXIS': int(section.get('MAX_SPLITS_IN_Y_AXIS', 5)),
            
            # Quantidade de lotes
            'MIN_AMOUNT_OF_LOTS': int(section.get('MIN_AMOUNT_OF_LOTS', 45)),
            
            # Dimensões dos lotes
            'MIN_LOT_WIDTH': int(section.get('MIN_LOT_WIDTH', 125)),
            'MIN_LOT_HEIGHT': int(section.get('MIN_LOT_HEIGHT', 155)),
            'MAX_LOT_WIDTH': int(section.get('MAX_LOT_WIDTH', 1000)),
            'MAX_LOT_HEIGHT': int(section.get('MAX_LOT_HEIGHT', 1000)),
            
            # Posições do quadrilátero inicial
            'QUAD_TOP_LEFT_X': float(section.get('QUAD_TOP_LEFT_X', 100)),
            'QUAD_TOP_LEFT_Y': float(section.get('QUAD_TOP_LEFT_Y', 200)),
            'QUAD_TOP_RIGHT_X': float(section.get('QUAD_TOP_RIGHT_X', 600)),
            'QUAD_TOP_RIGHT_Y': float(section.get('QUAD_TOP_RIGHT_Y', 200)),
            'QUAD_BOTTOM_RIGHT_X': float(section.get('QUAD_BOTTOM_RIGHT_X', 650)),
            'QUAD_BOTTOM_RIGHT_Y': float(section.get('QUAD_BOTTOM_RIGHT_Y', 1200)),
            'QUAD_BOTTOM_LEFT_X': float(section.get('QUAD_BOTTOM_LEFT_X', 150)),
            'QUAD_BOTTOM_LEFT_Y': float(section.get('QUAD_BOTTOM_LEFT_Y', 1100)),
            
            # Seed para aleatoriedade
            'SEED': int(section.get('SEED', 333)),
        }
        
        return config
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Obtém um valor de configuração.
        
        Args:
            key: Chave da configuração
            default: Valor padrão se não encontrado
            
        Returns:
            Valor da configuração
        """
        return self.config.get(key, default)
    
    def get_all(self) -> Dict[str, Any]:
        """
        Retorna todas as configurações.
        
        Returns:
            Dicionário com todas as configurações
        """
        return self.config.copy()
    
    def print_config(self):
        """Imprime todas as configurações de forma organizada."""
        print("\n" + "="*60)
        print("CONFIGURAÇÕES BSP")
        print("="*60)
        
        print("\n📐 Dimensões da Imagem:")
        print(f"  Largura: {self.config['IMAGE_WIDTH']}px")
        print(f"  Altura: {self.config['IMAGE_HEIGHT']}px")
        
        print("\n🔀 Subdivisões (Splits):")
        print(f"  Eixo X: {self.config['MIN_SPLITS_IN_X_AXIS']} a {self.config['MAX_SPLITS_IN_X_AXIS']}")
        print(f"  Eixo Y: {self.config['MIN_SPLITS_IN_Y_AXIS']} a {self.config['MAX_SPLITS_IN_Y_AXIS']}")
        
        print("\n📦 Lotes:")
        print(f"  Quantidade mínima: {self.config['MIN_AMOUNT_OF_LOTS']}")
        print(f"  Largura: {self.config['MIN_LOT_WIDTH']}px a {self.config['MAX_LOT_WIDTH']}px")
        print(f"  Altura: {self.config['MIN_LOT_HEIGHT']}px a {self.config['MAX_LOT_HEIGHT']}px")
        
        print("\n🔷 Quadrilátero Inicial:")
        print(f"  Superior Esquerdo: ({self.config['QUAD_TOP_LEFT_X']}, {self.config['QUAD_TOP_LEFT_Y']})")
        print(f"  Superior Direito: ({self.config['QUAD_TOP_RIGHT_X']}, {self.config['QUAD_TOP_RIGHT_Y']})")
        print(f"  Inferior Direito: ({self.config['QUAD_BOTTOM_RIGHT_X']}, {self.config['QUAD_BOTTOM_RIGHT_Y']})")
        print(f"  Inferior Esquerdo: ({self.config['QUAD_BOTTOM_LEFT_X']}, {self.config['QUAD_BOTTOM_LEFT_Y']})")
        
        print(f"\n🎲 Seed: {self.config['SEED']}")
        print("="*60 + "\n")
    
    def validate(self) -> tuple[bool, list[str]]:
        """
        Valida as configurações.
        
        Returns:
            Tupla (válido, lista de erros)
        """
        errors = []
        
        # Valida dimensões da imagem
        if self.config['IMAGE_WIDTH'] <= 0 or self.config['IMAGE_HEIGHT'] <= 0:
            errors.append("Dimensões da imagem devem ser positivas")
        
        # Valida splits
        if self.config['MIN_SPLITS_IN_X_AXIS'] > self.config['MAX_SPLITS_IN_X_AXIS']:
            errors.append("MIN_SPLITS_IN_X_AXIS deve ser <= MAX_SPLITS_IN_X_AXIS")
        if self.config['MIN_SPLITS_IN_Y_AXIS'] > self.config['MAX_SPLITS_IN_Y_AXIS']:
            errors.append("MIN_SPLITS_IN_Y_AXIS deve ser <= MAX_SPLITS_IN_Y_AXIS")
        
        # Valida dimensões dos lotes
        if self.config['MIN_LOT_WIDTH'] > self.config['MAX_LOT_WIDTH']:
            errors.append("MIN_LOT_WIDTH deve ser <= MAX_LOT_WIDTH")
        if self.config['MIN_LOT_HEIGHT'] > self.config['MAX_LOT_HEIGHT']:
            errors.append("MIN_LOT_HEIGHT deve ser <= MAX_LOT_HEIGHT")
        
        # Valida quadrilátero dentro da imagem
        coords = [
            (self.config['QUAD_TOP_LEFT_X'], self.config['QUAD_TOP_LEFT_Y']),
            (self.config['QUAD_TOP_RIGHT_X'], self.config['QUAD_TOP_RIGHT_Y']),
            (self.config['QUAD_BOTTOM_RIGHT_X'], self.config['QUAD_BOTTOM_RIGHT_Y']),
            (self.config['QUAD_BOTTOM_LEFT_X'], self.config['QUAD_BOTTOM_LEFT_Y']),
        ]
        
        for i, (x, y) in enumerate(coords):
            if x < 0 or x > self.config['IMAGE_WIDTH']:
                errors.append(f"Vértice {i+1}: X={x} está fora da imagem (0-{self.config['IMAGE_WIDTH']})")
            if y < 0 or y > self.config['IMAGE_HEIGHT']:
                errors.append(f"Vértice {i+1}: Y={y} está fora da imagem (0-{self.config['IMAGE_HEIGHT']})")
        
        return (len(errors) == 0, errors)


def create_default_config(filename: str = "config_bsp.ini"):
    """
    Cria um arquivo de configuração padrão.
    
    Args:
        filename: Nome do arquivo a criar
    """
    default_content = """;========================================
; Configuração BSP - Binary Space Partitioning
; Subdivisão automática de lotes urbanos
;========================================

;tamanho geral da imagem gerada (lembrando que as posições do quadrilatero precisam estar dentro desse tamanho)
IMAGE_WIDTH=1300
IMAGE_HEIGHT=1300
;quantidade minima de splits pelo bsp em cada "espaço quadrilatero"
MIN_SPLITS_IN_X_AXIS=1
MIN_SPLITS_IN_Y_AXIS=1
;quantidade maxima de splits, mesma logica acima
MAX_SPLITS_IN_X_AXIS=5
MAX_SPLITS_IN_Y_AXIS=5
;quantidade minima de lotes/separações (não necessariamente vai conseguir chegar lá - depende dos outros parametros tbm)
MIN_AMOUNT_OF_LOTS=45
;dimensões minimas pra cada lote
MIN_LOT_WIDTH=125
MIN_LOT_HEIGHT=155
;dimensões máximas pra cada lote
MAX_LOT_WIDTH=1000
MAX_LOT_HEIGHT=1000
;posicoes do retangulo inicial abaixo:
QUAD_TOP_LEFT_X=100
QUAD_TOP_LEFT_Y=200
QUAD_TOP_RIGHT_X=600
QUAD_TOP_RIGHT_Y=200
QUAD_BOTTOM_RIGHT_X=650
QUAD_BOTTOM_RIGHT_Y=1200
QUAD_BOTTOM_LEFT_X=150
QUAD_BOTTOM_LEFT_Y=1100
;mudar a seed para de repente gerar resultados diferentes a cada rodagem
SEED=333
"""
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(default_content)
    
    print(f"✅ Arquivo de configuração padrão criado: {filename}")


if __name__ == "__main__":
    # Testa o parser
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--create":
        create_default_config()
    else:
        try:
            config = BSPConfig()
            config.print_config()
            
            valid, errors = config.validate()
            if valid:
                print("✅ Configuração válida!")
            else:
                print("❌ Erros encontrados:")
                for error in errors:
                    print(f"  - {error}")
        except FileNotFoundError:
            print("❌ Arquivo config_bsp.ini não encontrado!")
            print("Execute: python config_parser.py --create")
        except Exception as e:
            print(f"❌ Erro: {e}")