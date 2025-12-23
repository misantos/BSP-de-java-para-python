import numpy as np
from PIL import Image, ImageDraw
import random
import math
from typing import List, Tuple
import argparse


class Lote:
    """Representa um lote retangular que será otimizado no mapa."""
    
    todos_lotes: List['Lote'] = []
    imagem_fundo: np.ndarray = None
    iteration: int = 0
    MAX_IT: int = 8000
    fitness_index: int = 0
    
    # Constantes
    PIXEL_POR_METRO = 5.4  # 108 pixels <-> 20m
    AREA_MIN = 120 * (PIXEL_POR_METRO ** 2)  # m²
    
    def __init__(self):
        """Inicializa um novo lote com dimensões e posição aleatórias."""
        self.altura: float = 0
        self.largura: float = 0
        self.x: float = 0
        self.y: float = 0
        self.lote_esquina: bool = False
        self.fitness: List[float] = [0.0, 0.0]
        self.iteracoes_andar: int = 0
        
        Lote.todos_lotes.append(self)
        self._inicializar()
    
    def _inicializar(self):
        """Gera dimensões e posição aleatórias válidas para o lote."""
        # Gerar dimensões válidas
        while (self.altura * self.largura < self.AREA_MIN or 
               self.altura < self.largura * 0.15 or 
               self.largura < self.altura * 0.15 or 
               self.largura < 3 or self.altura < 3):
            self.altura = random.random() * 30 * self.PIXEL_POR_METRO
            self.largura = random.random() * 30 * self.PIXEL_POR_METRO
        
        # Posição aleatória
        img_height, img_width = self.imagem_fundo.shape[:2]
        self.x = random.random() * (img_width - self.largura)
        self.y = random.random() * (img_height - self.altura)
        self.lote_esquina = random.random() > 0.5
        
        self.calcular_fitness()
    
    @staticmethod
    def e_pixel_vermelho(x: float, y: float) -> bool:
        """Verifica se o pixel na posição (x, y) é vermelho."""
        if (x < 0 or y < 0 or 
            x >= Lote.imagem_fundo.shape[1] or 
            y >= Lote.imagem_fundo.shape[0]):
            return False
        
        pixel = Lote.imagem_fundo[int(y), int(x)]
        return pixel[0] > 240 and pixel[1] < 2 and pixel[2] < 2
    
    @staticmethod
    def set_imagem(imagem: np.ndarray):
        """Define a imagem de fundo para todos os lotes."""
        Lote.imagem_fundo = imagem
    
    @staticmethod
    def distancia_euclidiana(x1: float, y1: float, x2: float, y2: float) -> float:
        """Calcula a distância euclidiana entre dois pontos."""
        return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
    
    @staticmethod
    def podar():
        """Remove lotes com fitness negativo e reduz a população."""
        QTD_MIN = 15
        
        # Remove lotes com fitness negativo
        k = len(Lote.todos_lotes) - 1
        while k >= 0:
            if (Lote.todos_lotes[k].fitness[Lote.fitness_index] < 0 and 
                len(Lote.todos_lotes) > QTD_MIN):
                Lote.todos_lotes.pop(k)
                k -= 2
            else:
                k -= 2
        
        # Remove últimos lotes até 93% do tamanho anterior
        tam_anterior = len(Lote.todos_lotes)
        while (len(Lote.todos_lotes) > 0.93 * tam_anterior and 
               len(Lote.todos_lotes) > QTD_MIN):
            Lote.todos_lotes.pop()
    
    @staticmethod
    def estrategia_elitista():
        """Clona os melhores lotes (estratégia elitista do algoritmo genético)."""
        if random.random() >= 0.95:
            return
        
        CLONE_MELHOR = 10
        for _ in range(CLONE_MELHOR):
            # Seleciona um dos melhores 20% lotes
            indice = int((len(Lote.todos_lotes) / 5) * random.random())
            lote_original = Lote.todos_lotes[indice]
            
            # Cria clone
            novo_lote = Lote.__new__(Lote)
            novo_lote.x = lote_original.x
            novo_lote.y = lote_original.y
            novo_lote.altura = lote_original.altura
            novo_lote.largura = lote_original.largura
            novo_lote.lote_esquina = lote_original.lote_esquina
            novo_lote.fitness = lote_original.fitness.copy()
            novo_lote.iteracoes_andar = 0
            
            Lote.todos_lotes.append(novo_lote)
            novo_lote.ordenar_lote()
            
            if random.random() < 0.3:
                Lote.podar()
    
    @staticmethod
    def area(x1: float, y1: float, x2: float, y2: float) -> float:
        """Calcula a área de um retângulo."""
        return (x2 - x1) * (y2 - y1)
    
    @staticmethod
    def uniao_area(lote1: 'Lote', lote2: 'Lote') -> float:
        """Calcula a área de interseção entre dois lotes."""
        quina_esq_cima_x = lote2.x
        quina_esq_cima_y = lote2.y
        
        if (quina_esq_cima_x > lote1.x and 
            quina_esq_cima_x < lote1.x + lote1.largura and
            quina_esq_cima_y > lote1.y and 
            quina_esq_cima_y < lote1.y + lote1.altura):
            return Lote.area(quina_esq_cima_x, quina_esq_cima_y, 
                           lote1.x + lote1.largura, lote1.y + lote1.altura)
        return 0
    
    def andar_randomicamente(self):
        """Move o lote aleatoriamente (random walk) para buscar melhor posição."""
        self.iteracoes_andar += 1
        pixel_movimento = 15
        previous_x, previous_y = self.x, self.y
        previous_fitness = self.fitness[self.fitness_index]
        
        # Busca global (mutação)
        if random.random() < 0.1:
            pixel_movimento = self.imagem_fundo.shape[1]
        
        # Movimento aleatório
        if random.random() < 0.3:
            self.x += -pixel_movimento + 2 * pixel_movimento * random.random()
        if random.random() < 0.3:
            self.y += -pixel_movimento + 2 * pixel_movimento * random.random()
        
        # Busca local
        aux_x = -1 + (2 * random.random() + 0.001)
        aux_y = -1 + (2 * random.random() + 0.001)
        self.x += aux_x
        self.y += aux_y
        
        # Verificar limites
        img_height, img_width = self.imagem_fundo.shape[:2]
        volta = (self.x < 0 or self.y < 0 or 
                self.x >= img_width or self.y >= img_height)
        
        volta2 = volta or (self.fitness_index > 0 and 
                          (self.e_pixel_vermelho(previous_x, previous_y) and 
                           not self.e_pixel_vermelho(self.x, self.y) or
                           self.e_pixel_vermelho(previous_x + self.largura, 
                                               previous_y + self.altura) and 
                           not self.e_pixel_vermelho(self.x + self.largura, 
                                                    self.y + self.altura)))
        
        # Se não melhorar, reverte
        self.calcular_fitness()
        if self.fitness[self.fitness_index] < previous_fitness or volta2:
            self.x = previous_x
            self.y = previous_y
            self.fitness[self.fitness_index] = previous_fitness
    
    def calcular_fitness(self):
        """Calcula o fitness do lote baseado em múltiplos critérios."""
        # Troca de fase após 40% das iterações
        if Lote.iteration > Lote.MAX_IT * 0.4 and Lote.fitness_index == 0:
            try:
                desenhar_todos_retangulos()
            except Exception as e:
                print(f"Erro ao desenhar: {e}")
            Lote.fitness_index = 1
        
        positivo = 0
        negativo = 0
        
        # Avalia pixels dentro do lote
        img_height, img_width = self.imagem_fundo.shape[:2]
        for i in range(int(self.y), int(self.y + self.altura)):
            if i < 0 or i >= img_height:
                negativo += 1
                continue
            
            for j in range(int(self.x), int(self.x + self.largura)):
                if j < 0 or j >= img_width:
                    negativo += 1
                    continue
                
                if self.e_pixel_vermelho(j, i):
                    positivo += 3
                else:
                    negativo += 4
        
        self.fitness[self.fitness_index] = positivo - negativo
        
        # Primeira fase: apenas posicionar no vermelho
        if self.fitness_index == 0:
            return
        
        # Segunda fase: refinar posicionamento
        # Penalizar interseções
        for lote in Lote.todos_lotes:
            if lote != self:
                negativo += self.uniao_area(self, lote)
        
        # Recompensar alinhamento de cantos
        thres = 5
        ADD = 200
        
        for lote in Lote.todos_lotes:
            if lote == self:
                continue
            
            pelo_menos_2 = 0
            ok = False
            
            # Alinhamento direita
            if self.distancia_euclidiana(self.x + self.largura, self.y, 
                                        lote.x, lote.y) < thres:
                pelo_menos_2 += 1
            if self.distancia_euclidiana(self.x + self.largura, self.y + self.altura,
                                        lote.x, lote.y + lote.altura) < thres:
                pelo_menos_2 += 1
            
            if pelo_menos_2 >= 2:
                positivo += ADD
                ok = True
            
            # Alinhamento esquerda
            if self.distancia_euclidiana(self.x, self.y, 
                                        lote.x + lote.largura, lote.y) < thres:
                pelo_menos_2 += 1
            if self.distancia_euclidiana(self.x, self.y + self.altura,
                                        lote.x + lote.largura, lote.y + lote.altura) < thres:
                pelo_menos_2 += 1
            
            if pelo_menos_2 >= 2:
                positivo += ADD
                ok = True
            
            pelo_menos_2 = 0
            
            # Alinhamento cima
            if self.distancia_euclidiana(self.x, self.y, 
                                        lote.x, lote.y + lote.altura) < thres:
                pelo_menos_2 += 1
            if self.distancia_euclidiana(self.x + self.largura, self.y,
                                        lote.x + lote.largura, lote.y + lote.altura) < thres:
                pelo_menos_2 += 1
            
            if pelo_menos_2 >= 2:
                positivo += ADD
                ok = True
            
            pelo_menos_2 = 0
            
            # Alinhamento baixo
            if self.distancia_euclidiana(self.x, self.y + self.altura,
                                        lote.x, lote.y) < thres:
                pelo_menos_2 += 1
            if self.distancia_euclidiana(self.x + self.largura, self.y + self.altura,
                                        lote.x + lote.largura, lote.y) < thres:
                pelo_menos_2 += 1
            
            if pelo_menos_2 >= 2:
                positivo += ADD
                ok = True
            
            if ok:
                break
        
        self.fitness[self.fitness_index] = positivo - negativo
    
    def pixel_dentro_do_lote(self, x: float, y: float) -> bool:
        """Verifica se um pixel está dentro do lote."""
        return (x > self.x and x < self.x + self.largura and 
                y > self.y and y < self.y + self.altura)
    
    def ordenar_lote(self):
        """Ordena o lote na lista baseado em seu fitness."""
        indice_atual = Lote.todos_lotes.index(self)
        for k in range(indice_atual, -1, -1):
            if self.fitness[self.fitness_index] > Lote.todos_lotes[k].fitness[self.fitness_index]:
                Lote.todos_lotes.pop(indice_atual)
                Lote.todos_lotes.insert(k, self)
                indice_atual = k
    
    def run(self):
        """Executa uma iteração do algoritmo (movimento + avaliação + ordenação)."""
        self.andar_randomicamente()
        self.calcular_fitness()
        self.ordenar_lote()


def desenhar_todos_retangulos(salvar_como: str = None):
    """Desenha todos os lotes na imagem e exibe/salva o resultado."""
    # Converte numpy array para PIL Image
    img_array = Lote.imagem_fundo.copy()
    img_pil = Image.fromarray(img_array)
    draw = ImageDraw.Draw(img_pil)
    
    # Desenha cada lote
    for lote in Lote.todos_lotes:
        x1, y1 = int(lote.x), int(lote.y)
        x2, y2 = int(lote.x + lote.largura), int(lote.y + lote.altura)
        draw.rectangle([x1, y1, x2, y2], outline=(0, 255, 0), width=2)
    
    # Salva ou mostra
    if salvar_como:
        img_pil.save(salvar_como)
        print(f"Imagem salva em: {salvar_como}")
    else:
        img_pil.show()


def main():
    """Função principal que executa o algoritmo genético."""
    parser = argparse.ArgumentParser(description='Otimização de lotes usando algoritmo genético')
    parser.add_argument('imagem', type=str, help='Caminho para a imagem de entrada')
    parser.add_argument('--lotes', type=int, default=150, help='Número total de lotes')
    parser.add_argument('--iteracoes', type=int, default=8000, help='Número de iterações')
    parser.add_argument('--output', type=str, help='Caminho para salvar a imagem final')
    
    args = parser.parse_args()
    
    # Carrega imagem
    print(f"Carregando imagem: {args.imagem}")
    image = Image.open(args.imagem)
    image_array = np.array(image)
    
    # Inicializa
    TOTAL_LOTES = args.lotes
    Lote.set_imagem(image_array)
    
    # Cria lotes iniciais
    print(f"Criando {TOTAL_LOTES} lotes...")
    for _ in range(TOTAL_LOTES):
        Lote()
    
    # Executa algoritmo genético
    Lote.MAX_IT = args.iteracoes
    print(f"Executando {Lote.MAX_IT} iterações...")
    
    for iteration in range(Lote.MAX_IT + 1):
        Lote.iteration = iteration
        
        # Executa uma iteração para cada lote
        for lote in Lote.todos_lotes:
            lote.run()
        
        # Aplica estratégia elitista
        Lote.estrategia_elitista()
        
        # Desenha progresso a cada 2000 iterações
        if iteration > 0 and iteration % 2000 == 0:
            print(f"Iteração {iteration}/{Lote.MAX_IT}")
            desenhar_todos_retangulos(f"progresso_{iteration}.png")
    
    # Resultado final
    print("Otimização concluída!")
    output_file = args.output or "resultado_final.png"
    desenhar_todos_retangulos(output_file)
    print(f"Total de lotes finais: {len(Lote.todos_lotes)}")


if __name__ == "__main__":
    main()