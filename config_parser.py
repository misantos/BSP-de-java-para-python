"""
config_parser.py - Parser de configuração do BSP

Lê arquivos .ini e retorna dicionário de configuração.
CORRIGIDO: parser.optionxform = str para preservar maiúsculas

Autor: Refatoração Python
Data: 2026-01-07
"""

import configparser
from typing import Dict, Any, Tuple, List
import os


class BSPConfig:
    """
    Gerencia configurações do algoritmo BSP.
    
    Lê arquivo .ini e fornece acesso aos parâmetros.
    """
    
    # Valores padrão
    DEFAULTS = {
        'IMAGE_WIDTH': 1300,
        'IMAGE_HEIGHT': 1300,
        'SEED': None,  # Agora é opcional!
        
        # Quadrilátero inicial
        'QUAD_TOP_LEFT_X': 100,
        'QUAD_TOP_LEFT_Y': 200,
        'QUAD_TOP_RIGHT_X': 600,
        'QUAD_TOP_RIGHT_Y': 200,
        'QUAD_BOTTOM_RIGHT_X': 650,
        'QUAD_BOTTOM_RIGHT_Y': 1200,
        'QUAD_BOTTOM_LEFT_X': 150,
        'QUAD_BOTTOM_LEFT_Y': 1100,
        
        # Limites de lotes
        'MIN_AMOUNT_OF_LOTS': 45,
        'MIN_LOT_HEIGHT': 155,
        'MIN_LOT_WIDTH': 125,
        'MAX_LOT_HEIGHT': 1000,
        'MAX_LOT_WIDTH': 1000,
        
        # Limites de subdivisões
        'MIN_SPLITS_IN_X_AXIS': 1,
        'MAX_SPLITS_IN_X_AXIS': 5,
        'MIN_SPLITS_IN_Y_AXIS': 1,
        'MAX_SPLITS_IN_Y_AXIS': 5,
    }
    
    def __init__(self, config_file: str = 'config_bsp.ini'):
        """
        Inicializa o parser de configuração.
        
        Args:
            config_file: Caminho para o arquivo .ini
        """
        self.config_file = config_file
        self._config = self._read_config()
    
    def _read_config(self) -> Dict[str, Any]:
        """
        Lê o arquivo de configuração.
        
        Returns:
            Dicionário com valores de configuração
        """
        parser = configparser.ConfigParser()
        
        # ⚠️ IMPORTANTE: Preserva maiúsculas/minúsculas nas chaves
        parser.optionxform = str
        
        # Verifica se arquivo existe
        if not os.path.exists(self.config_file):
            print(f"⚠️  Arquivo {self.config_file} não encontrado. Usando valores padrão.")
            return dict(self.DEFAULTS)
        
        # Lê o arquivo
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Adiciona seção [DEFAULT] se não existir
            if not content.strip().startswith('['):
                content = '[DEFAULT]\n' + content
            
            parser.read_string(content)
        except Exception as e:
            print(f"❌ Erro ao ler {self.config_file}: {e}")
            return dict(self.DEFAULTS)
        
        # Obtém a seção (DEFAULT ou primeira disponível)
        if parser.sections():
            section = parser[parser.sections()[0]]
        else:
            section = parser['DEFAULT']
        
        # Monta dicionário de configuração
        config = {}
        
        for key, default_value in self.DEFAULTS.items():
            if key in section:
                raw_value = section[key]
                
                # Converte para o tipo correto
                if default_value is None:
                    # SEED é opcional - None ou int
                    if raw_value.lower() in ('none', 'null', ''):
                        config[key] = None
                    else:
                        try:
                            config[key] = int(raw_value)
                        except ValueError:
                            config[key] = None
                elif isinstance(default_value, int):
                    try:
                        config[key] = int(raw_value)
                    except ValueError:
                        config[key] = default_value
                elif isinstance(default_value, float):
                    try:
                        config[key] = float(raw_value)
                    except ValueError:
                        config[key] = default_value
                else:
                    config[key] = raw_value
            else:
                config[key] = default_value
        
        return config
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Obtém um valor de configuração.
        
        Args:
            key: Chave da configuração
            default: Valor padrão se não existir
            
        Returns:
            Valor da configuração
        """
        return self._config.get(key, default)
    
    def get_all(self) -> Dict[str, Any]:
        """
        Retorna todas as configurações.
        
        Returns:
            Dicionário com todas as configurações
        """
        return dict(self._config)
    
    def validate(self) -> Tuple[bool, List[str]]:
        """
        Valida as configurações.
        
        Returns:
            (is_valid, list_of_errors)
        """
        errors = []
        
        # Valida dimensões da imagem
        if self._config['IMAGE_WIDTH'] <= 0:
            errors.append("IMAGE_WIDTH deve ser > 0")
        if self._config['IMAGE_HEIGHT'] <= 0:
            errors.append("IMAGE_HEIGHT deve ser > 0")
        
        # Valida limites de lotes
        if self._config['MIN_LOT_WIDTH'] <= 0:
            errors.append("MIN_LOT_WIDTH deve ser > 0")
        if self._config['MIN_LOT_HEIGHT'] <= 0:
            errors.append("MIN_LOT_HEIGHT deve ser > 0")
        if self._config['MIN_LOT_WIDTH'] > self._config['MAX_LOT_WIDTH']:
            errors.append("MIN_LOT_WIDTH não pode ser maior que MAX_LOT_WIDTH")
        if self._config['MIN_LOT_HEIGHT'] > self._config['MAX_LOT_HEIGHT']:
            errors.append("MIN_LOT_HEIGHT não pode ser maior que MAX_LOT_HEIGHT")
        
        # Valida limites de subdivisões
        if self._config['MIN_SPLITS_IN_X_AXIS'] < 1:
            errors.append("MIN_SPLITS_IN_X_AXIS deve ser >= 1")
        if self._config['MIN_SPLITS_IN_Y_AXIS'] < 1:
            errors.append("MIN_SPLITS_IN_Y_AXIS deve ser >= 1")
        if self._config['MIN_SPLITS_IN_X_AXIS'] > self._config['MAX_SPLITS_IN_X_AXIS']:
            errors.append("MIN_SPLITS_IN_X_AXIS não pode ser maior que MAX_SPLITS_IN_X_AXIS")
        if self._config['MIN_SPLITS_IN_Y_AXIS'] > self._config['MAX_SPLITS_IN_Y_AXIS']:
            errors.append("MIN_SPLITS_IN_Y_AXIS não pode ser maior que MAX_SPLITS_IN_Y_AXIS")
        
        return (len(errors) == 0, errors)
    
    def print_config(self) -> None:
        """Imprime as configurações de forma formatada."""
        print("\n" + "=" * 60)
        print("📋 CONFIGURAÇÕES DO BSP")
        print("=" * 60)
        
        # SEED no topo (destaque)
        seed_value = self._config.get('SEED')
        if seed_value is not None:
            print(f"\n🎲 SEED: {seed_value}")
        else:
            print(f"\n🎲 SEED: Aleatória (não definida)")
        
        # Imagem
        print(f"\n📐 Imagem:")
        print(f"   Largura: {self._config['IMAGE_WIDTH']} px")
        print(f"   Altura:  {self._config['IMAGE_HEIGHT']} px")
        
        # Quadrilátero inicial
        print(f"\n📍 Quadrilátero inicial:")
        print(f"   Top Left:     ({self._config['QUAD_TOP_LEFT_X']}, {self._config['QUAD_TOP_LEFT_Y']})")
        print(f"   Top Right:    ({self._config['QUAD_TOP_RIGHT_X']}, {self._config['QUAD_TOP_RIGHT_Y']})")
        print(f"   Bottom Right: ({self._config['QUAD_BOTTOM_RIGHT_X']}, {self._config['QUAD_BOTTOM_RIGHT_Y']})")
        print(f"   Bottom Left:  ({self._config['QUAD_BOTTOM_LEFT_X']}, {self._config['QUAD_BOTTOM_LEFT_Y']})")
        
        # Limites de lotes
        print(f"\n📦 Limites de lotes:")
        print(f"   Mínimo de lotes: {self._config['MIN_AMOUNT_OF_LOTS']}")
        print(f"   Largura:  {self._config['MIN_LOT_WIDTH']} - {self._config['MAX_LOT_WIDTH']} px")
        print(f"   Altura:   {self._config['MIN_LOT_HEIGHT']} - {self._config['MAX_LOT_HEIGHT']} px")
        
        # Limites de subdivisões
        print(f"\n✂️  Limites de subdivisões:")
        print(f"   Eixo X: {self._config['MIN_SPLITS_IN_X_AXIS']} - {self._config['MAX_SPLITS_IN_X_AXIS']}")
        print(f"   Eixo Y: {self._config['MIN_SPLITS_IN_Y_AXIS']} - {self._config['MAX_SPLITS_IN_Y_AXIS']}")
        
        print("\n" + "=" * 60)
    
    def to_lot_stack_config(self) -> Dict[str, Any]:
        """
        Converte para o formato esperado pelo LotStack.
        
        Returns:
            Dicionário no formato do LotStack
        """
        return {
            'MIN_LOTS': self._config['MIN_AMOUNT_OF_LOTS'],
            'MIN_HEIGHT_LOT': self._config['MIN_LOT_HEIGHT'],
            'MIN_WIDTH_LOT': self._config['MIN_LOT_WIDTH'],
            'MAX_HEIGHT_LOT': self._config['MAX_LOT_HEIGHT'],
            'MAX_WIDTH_LOT': self._config['MAX_LOT_WIDTH'],
            'MIN_SPLIT_X': self._config['MIN_SPLITS_IN_X_AXIS'],
            'MAX_SPLIT_X': self._config['MAX_SPLITS_IN_X_AXIS'],
            'MIN_SPLIT_Y': self._config['MIN_SPLITS_IN_Y_AXIS'],
            'MAX_SPLIT_Y': self._config['MAX_SPLITS_IN_Y_AXIS'],
            'SEED': self._config['SEED'],
        }


# Teste do módulo
if __name__ == "__main__":
    print("🧪 Testando config_parser.py")
    
    # Testa com valores padrão (sem arquivo)
    config = BSPConfig('arquivo_inexistente.ini')
    config.print_config()
    
    # Valida
    is_valid, errors = config.validate()
    print(f"\n✅ Configuração válida: {is_valid}")
    if errors:
        for error in errors:
            print(f"   ❌ {error}")
    
    # Testa conversão para LotStack
    lot_stack_config = config.to_lot_stack_config()
    print(f"\n📋 Configuração para LotStack:")
    for key, value in lot_stack_config.items():
        print(f"   {key}: {value}")