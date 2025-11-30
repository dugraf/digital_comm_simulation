import numpy as np

def manchester_encode(bits: np.ndarray) -> np.ndarray:
    """
    Codificação Manchester:
    0 -> [1, -1] (Alto-Baixo)
    1 -> [-1, 1] (Baixo-Alto)
    """
    encoded = []
    for bit in bits:
        if bit == 0:
            encoded.extend([1, -1])
        else:
            encoded.extend([-1, 1])
    return np.array(encoded)

def manchester_decode(signal: np.ndarray) -> np.ndarray:
    """
    Decodifica Manchester observando a transição.
    Lê pares de amostras.
    """
    decoded_bits = []
    # Percorre de 2 em 2
    for i in range(0, len(signal), 2):
        if i+1 >= len(signal): break
        
        val1 = signal[i]
        val2 = signal[i+1]
        
        # Regra de decisão baseada na diferença
        # Se val1 > val2 (desceu), era 0. Se val1 < val2 (subiu), era 1.
        if val1 > val2:
            decoded_bits.append(0)
        else:
            decoded_bits.append(1)
            
    return np.array(decoded_bits)