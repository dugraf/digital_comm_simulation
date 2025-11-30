import numpy as np

# --- BPSK ---
def bpsk_modulate(bits: np.ndarray) -> np.ndarray:
    """0 -> +1, 1 -> -1"""
    return np.where(bits == 0, 1.0, -1.0)

def bpsk_demodulate(received_signal: np.ndarray) -> np.ndarray:
    """Se > 0 é bit 0, se < 0 é bit 1"""
    # np.real garante que funcione mesmo se vier ruído complexo
    return np.where(np.real(received_signal) > 0, 0, 1)

# --- 16-QAM ---
# Tabela de mapeamento Gray (Bit Pattern -> Complex Value)
# Normalizado por sqrt(10) para energia unitária
NORM_FACTOR = np.sqrt(10)
QAM_MAP = {
    (0,0,0,0): 3+3j, (0,0,0,1): 3+1j, (0,0,1,1): 3-1j, (0,0,1,0): 3-3j,
    (0,1,0,0): 1+3j, (0,1,0,1): 1+1j, (0,1,1,1): 1-1j, (0,1,1,0): 1-3j,
    (1,1,0,0):-1+3j, (1,1,0,1):-1+1j, (1,1,1,1):-1-1j, (1,1,1,0):-1-3j,
    (1,0,0,0):-3+3j, (1,0,0,1):-3+1j, (1,0,1,1):-3-1j, (1,0,1,0):-3-3j
}
# Pré-calcula os pontos da constelação para o demodulador
CONSTELLATION_POINTS = list(QAM_MAP.values())
CONSTELLATION_BITS = list(QAM_MAP.keys())

def qam16_modulate(bits: np.ndarray) -> np.ndarray:
    # Padding para garantir múltiplo de 4
    pad_len = (4 - (len(bits) % 4)) % 4
    bits_padded = np.pad(bits, (0, pad_len), 'constant')
    
    symbols = []
    # Processa 4 bits por vez
    for i in range(0, len(bits_padded), 4):
        quad = tuple(bits_padded[i:i+4])
        # Busca na tabela e normaliza
        sym = QAM_MAP[quad] / NORM_FACTOR
        symbols.append(sym)
        
    return np.array(symbols)

def qam16_demodulate(received_signal: np.ndarray, original_length: int) -> np.ndarray:
    decoded_bits = []
    
    # Normalização inversa para comparar com a tabela (multiplica por sqrt(10))
    received_scaled = received_signal * NORM_FACTOR
    
    for rx_sym in received_scaled:
        # Algoritmo de Distância Mínima:
        # Calcula a distância do símbolo recebido para TODOS os 16 pontos ideais
        distances = [abs(rx_sym - pt) for pt in CONSTELLATION_POINTS]
        
        # Pega o índice do ponto mais próximo
        min_idx = np.argmin(distances)
        
        # Recupera os 4 bits associados àquele ponto
        bits_tuple = CONSTELLATION_BITS[min_idx]
        decoded_bits.extend(bits_tuple)
        
    # Remove padding e retorna
    return np.array(decoded_bits[:original_length])