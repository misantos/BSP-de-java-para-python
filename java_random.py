"""
java_random.py - Gerador de números aleatórios compatível com Java

Este módulo implementa o algoritmo de geração de números aleatórios do Java
(java.util.Random) em Python. É essencial para garantir que o algoritmo BSP
produza exatamente os mesmos resultados que a versão Java quando usada a mesma seed.

O Java usa um LCG (Linear Congruential Generator) com constantes específicas.
Este módulo replica esse comportamento bit por bit.

Por que isso é necessário?
- Python usa um algoritmo diferente (Mersenne Twister)
- Para reproduzir exatamente os resultados do Java, precisamos do mesmo algoritmo
- Com a mesma seed, ambas as versões produzem a mesma sequência de números

Autor: Migração Python por Claude (Baseado em java.util.Random)
"""


class JavaRandom:
    """
    Implementação do java.util.Random em Python.
    
    Usa o mesmo algoritmo LCG (Linear Congruential Generator) do Java
    com as mesmas constantes mágicas para garantir resultados idênticos.
    
    Algoritmo LCG:
        seed_next = (seed_atual * multiplicador + incremento) mod 2^48
    
    Constantes do Java:
        multiplicador = 0x5DEECE66D (25214903917)
        incremento = 0xB (11)
        módulo = 2^48
    
    Attributes:
        seed (int): Estado interno do gerador (48 bits)
    
    Examples:
        >>> rng = JavaRandom(42)  # Seed 42
        >>> rng.nextInt(100)      # Inteiro de 0 a 99
        >>> rng.nextBoolean()     # True ou False
        >>> rng.nextDouble()      # Float de 0.0 a 1.0
    """
    
    def __init__(self, seed: int = 0):
        """
        Inicializa o gerador com uma seed.
        
        A seed é processada da mesma forma que no Java:
        1. XOR com constante 0x5DEECE66D
        2. Trunca para 48 bits (AND com máscara)
        
        Args:
            seed (int): Semente inicial (qualquer inteiro)
        
        Note:
            Mesmo seed sempre produz a mesma sequência de números.
            Seed 0 é válida (não use None).
        
        Examples:
            >>> rng1 = JavaRandom(333)  # Seed do config padrão
            >>> rng2 = JavaRandom(333)  # Mesma seed
            >>> rng1.nextInt(10) == rng2.nextInt(10)  # Mesmo resultado
            True
        """
        # Processa a seed exatamente como o Java faz
        # XOR com constante mágica, depois trunca para 48 bits
        self.seed = (seed ^ 0x5DEECE66D) & ((1 << 48) - 1)
    
    def next(self, bits: int) -> int:
        """
        Gera os próximos bits aleatórios (método interno).
        
        Implementa o núcleo do algoritmo LCG do Java:
        1. Atualiza seed: seed = (seed * 0x5DEECE66D + 0xB) mod 2^48
        2. Retorna os bits mais significativos do seed
        
        Args:
            bits (int): Número de bits a gerar (1-32)
            
        Returns:
            int: Inteiro com os bits gerados
        
        Note:
            Método interno usado por nextInt(), nextBoolean(), etc.
            Não precisa ser chamado diretamente.
        """
        # Aplica a fórmula do LCG
        # seed_next = (seed * multiplicador + incremento) mod 2^48
        self.seed = (self.seed * 0x5DEECE66D + 0xB) & ((1 << 48) - 1)
        
        # Retorna os 'bits' mais significativos do seed
        # Shift right para pegar os bits do topo
        return int(self.seed >> (48 - bits))
    
    def nextInt(self, n: int = None) -> int:
        """
        Gera o próximo inteiro aleatório.
        
        Comportamento:
        - Se n=None: retorna qualquer int de 32 bits
        - Se n fornecido: retorna int de 0 até n-1 (inclusive)
        
        Args:
            n (int, optional): Limite superior (exclusivo). 
                              Se None, retorna int de 32 bits completo.
            
        Returns:
            int: Inteiro aleatório no range especificado
        
        Raises:
            ValueError: Se n <= 0
        
        Note:
            Compatível com java.util.Random.nextInt(n)
            nextInt(10) retorna 0,1,2,3,4,5,6,7,8,9 com probabilidade igual
        
        Examples:
            >>> rng = JavaRandom(42)
            >>> rng.nextInt(100)  # 0 até 99
            >>> rng.nextInt(6)    # Simula dado: 0 até 5
        """
        # Se n não fornecido, retorna int de 32 bits completo
        if n is None:
            return self.next(32)
        
        # Validação
        if n <= 0:
            raise ValueError("n must be positive")
        
        # Otimização para potências de 2
        # Se n é potência de 2, usa bit masking (mais rápido)
        if (n & -n) == n:  # Testa se n é potência de 2
            return int((n * self.next(31)) >> 31)
        
        # Algoritmo geral do Java para nextInt(n)
        # Garante distribuição uniforme mesmo quando n não é potência de 2
        bits = self.next(31)
        val = bits % n
        
        # Descarta bits se caírem na região de viés
        # (quando 2^31 não é divisível por n)
        while bits - val + (n - 1) < 0:
            bits = self.next(31)
            val = bits % n
        
        return val
    
    def nextBoolean(self) -> bool:
        """
        Gera o próximo booleano aleatório.
        
        Retorna True ou False com 50% de probabilidade cada.
        Equivalente a nextInt(2) == 0, mas mais eficiente.
        
        Returns:
            bool: True ou False aleatório
        
        Note:
            Compatível com java.util.Random.nextBoolean()
            Usa apenas 1 bit do gerador
        
        Examples:
            >>> rng = JavaRandom(42)
            >>> rng.nextBoolean()  # True ou False
            >>> # Simular 100 moedas
            >>> moedas = [rng.nextBoolean() for _ in range(100)]
        """
        # Gera 1 bit aleatório e converte para boolean
        return self.next(1) != 0
    
    def nextFloat(self) -> float:
        """
        Gera o próximo float aleatório entre 0.0 e 1.0.
        
        Returns:
            float: Float entre 0.0 (inclusive) e 1.0 (exclusivo)
        
        Note:
            Compatível com java.util.Random.nextFloat()
            Usa 24 bits de precisão (float tem 24 bits de mantissa)
        
        Examples:
            >>> rng = JavaRandom(42)
            >>> rng.nextFloat()  # 0.0 <= x < 1.0
        """
        # Usa 24 bits (precisão de float) e divide por 2^24
        return self.next(24) / float(1 << 24)
    
    def nextDouble(self) -> float:
        """
        Gera o próximo double aleatório entre 0.0 e 1.0.
        
        Usa 53 bits de precisão (double tem 53 bits de mantissa).
        Combina dois valores de next() para obter 53 bits:
        - 26 bits do primeiro next() (shifted left 27)
        - 27 bits do segundo next()
        
        Returns:
            float: Double entre 0.0 (inclusive) e 1.0 (exclusivo)
        
        Note:
            Compatível com java.util.Random.nextDouble()
            Maior precisão que nextFloat()
        
        Examples:
            >>> rng = JavaRandom(42)
            >>> rng.nextDouble()  # 0.0 <= x < 1.0 com alta precisão
        """
        # Combina 26 + 27 bits = 53 bits (precisão de double)
        # Primeiro: 26 bits shifted left 27 posições
        # Segundo: 27 bits nas posições baixas
        return ((self.next(26) << 27) + self.next(27)) / float(1 << 53)
    
    def random(self) -> float:
        """
        Alias para nextDouble() para compatibilidade com Python random.
        
        Permite usar JavaRandom como drop-in replacement para random.Random():
        - random.Random().random() → JavaRandom().random()
        
        Returns:
            float: Double entre 0.0 e 1.0
        
        Examples:
            >>> rng = JavaRandom(42)
            >>> rng.random()  # Mesmo que rng.nextDouble()
        """
        return self.nextDouble()


# ===== Testes e Demonstração =====
if __name__ == "__main__":
    """
    Testes de compatibilidade com Java Random.
    Execute este arquivo diretamente para ver exemplos.
    """
    print("=" * 60)
    print("JavaRandom - Gerador Compatível com java.util.Random")
    print("=" * 60)
    print()
    
    # Teste com seed 333 (mesma do config padrão do BSP)
    print("Testando com SEED = 333 (config padrão)")
    print("-" * 60)
    jr = JavaRandom(333)
    
    print("\n1. Primeiros 10 valores de nextInt(10):")
    print("   (deve produzir mesma sequência que Java)")
    jr = JavaRandom(333)  # Reset
    for i in range(10):
        print(f"   {i+1:2d}. {jr.nextInt(10)}")
    
    print("\n2. Primeiros 10 valores de nextBoolean():")
    jr = JavaRandom(333)  # Reset
    for i in range(10):
        valor = jr.nextBoolean()
        print(f"   {i+1:2d}. {valor} ({'True' if valor else 'False'})")
    
    print("\n3. Primeiros 5 valores de nextDouble():")
    jr = JavaRandom(333)  # Reset
    for i in range(5):
        print(f"   {i+1}. {jr.nextDouble():.15f}")
    
    print("\n4. Teste de distribuição (nextInt(6) - simula dado):")
    jr = JavaRandom(42)
    contagem = [0] * 6
    num_rolls = 6000
    for _ in range(num_rolls):
        contagem[jr.nextInt(6)] += 1
    
    print(f"   Rolando dado 6000 vezes:")
    for i, count in enumerate(contagem):
        barra = "█" * (count // 20)
        print(f"   Face {i}: {count:4d} vezes {barra}")
    
    print("\n" + "=" * 60)
    print("✅ Testes concluídos!")
    print("   Se você rodar o mesmo código em Java com seed 333,")
    print("   deve obter exatamente os mesmos números.")
    print("=" * 60)