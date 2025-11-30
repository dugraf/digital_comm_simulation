import numpy as np

def str_to_bytes(message: str) -> bytes:
    message_bytes = message.encode('ascii', 'ignore')
    return message_bytes

def bytes_to_bit_vector(message_bytes: bytes) -> list:
    bit_vector = []
    for byte in message_bytes:
        binary_string = bin(byte)[2:].zfill(8)
        bit_vector.extend([int(bit) for bit in binary_string])
    return bit_vector

def manchester_encoding(bit_vector: list) -> list:
    manchester_signal = []
    
    for bit in bit_vector:
        if bit == 0:
            manchester_signal.extend([1, -1])
        else:
            manchester_signal.extend([-1, 1])
            
    return manchester_signal

def qam_16_modulation(bit_vector: list) -> np.ndarray:
    """
    Modulação 16-QAM: 4 bits por símbolo.
    Mapeia quartetos de bits para 16 símbolos (em 3 amplitudes diferentes).
    """
    # Adiciona padding se necessário para ser múltiplo de 4
    padding_needed = (4 - (len(bit_vector) % 4)) % 4
    bit_vector.extend([0] * padding_needed)
    
    # Agrupa os bits em quartetos (b1, b2, b3, b4)
    bit_quads = np.reshape(bit_vector, (-1, 4))
    
    # Mapeamento QAM (separando bits I e Q):
    # I-componente é determinado por b1 e b3
    # Q-componente é determinado por b2 e b4
    
    # Mapeamento Gray (exemplo para I e Q): 00->3, 01->1, 11->-1, 10->-3
    map_table = {0: 3, 1: 1, 3: -1, 2: -3} 
    
    I = np.zeros(len(bit_quads))
    Q = np.zeros(len(bit_quads))

    for i, (b1, b2, b3, b4) in enumerate(bit_quads):
        # Combinação I (b1 e b3)
        I_bits = b1 * 2 + b3 
        I[i] = map_table[I_bits]
        
        # Combinação Q (b2 e b4)
        Q_bits = b2 * 2 + b4
        Q[i] = map_table[Q_bits]
        
    # Símbolos complexos: I + j*Q. Normalizando pela energia (dividir por sqrt(10))
    symbols = (I + 1j * Q) / np.sqrt(10) 
    
    return symbols


def bpsk_modulation(bit_vector: list) -> np.ndarray:
    symbols = np.array([1 - 2*bit for bit in bit_vector])
    return symbols

def main():
    message = input("Digite a mensagem que deseja enviar: ")
    
    # 1. Conversão String para Bytes
    message_bytes = str_to_bytes(message)
    message_hex = ' '.join([f'0x{byte:02x}' for byte in message_bytes])
    print(f"\nMensagem em Hexadecimal: {message_hex}")

    # 1.1. Conversão Bytes para Vetor de Bits
    bit_vector = bytes_to_bit_vector(message_bytes)

    print("\nMensagem em Vetor de Bits:")
    print(f"{bit_vector[:64]} ... (Total de {len(bit_vector)} bits)")
    
    # 2. Codificação do canal (Manchester)
    manchester_signal = manchester_encoding(bit_vector)
    print("\nCodificação Manchester:")
    print(f"{manchester_signal[:64]} ... (Total de {len(manchester_signal)} valores)")

    # 3. Modulação (BPSK)
    bpsk_signal = bpsk_modulation(bit_vector)
    print("\nModulação BPSK:")
    print(f"{bpsk_signal[:64]} ... (Total de {len(bpsk_signal)} símbolos)")

    # 3.1 Modulação (16-QAM)
    qam_16_modulation_signal = qam_16_modulation(bit_vector)
    print("\nModulação 16-QAM:")
    print(f"{qam_16_modulation_signal[:16]} ... (Total de {len(qam_16_modulation_signal)} símbolos)")

if __name__ == "__main__":
    main()