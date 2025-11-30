import numpy as np

def str_to_bits(message: str) -> np.ndarray:
    """Converte string ASCII para vetor de bits numpy."""
    message_bytes = message.encode('ascii', 'ignore')
    bit_list = []
    for byte in message_bytes:
        # Converte para binário, remove o '0b' e preenche com zeros à esquerda até 8 bits
        binary_string = bin(byte)[2:].zfill(8)
        bit_list.extend([int(bit) for bit in binary_string])
    return np.array(bit_list)

def bits_to_str(bit_array: np.ndarray) -> str:
    """Reconverte vetor de bits para string."""
    # Garante que o array seja de inteiros
    bits = bit_array.astype(int)
    chars = []
    # Processa de 8 em 8 bits
    for i in range(0, len(bits), 8):
        byte_chunk = bits[i:i+8]
        if len(byte_chunk) < 8: break # Ignora bits incompletos no final
        
        # Converte array de bits para string "010101" e depois para int e char
        byte_str = "".join(str(b) for b in byte_chunk)
        chars.append(chr(int(byte_str, 2)))
    return "".join(chars)

def calculate_ber(sent_bits: np.ndarray, received_bits: np.ndarray) -> float:
    """Calcula a Taxa de Erro de Bit (BER)."""
    # Ajusta tamanhos caso haja padding
    min_len = min(len(sent_bits), len(received_bits))
    errors = np.sum(sent_bits[:min_len] != received_bits[:min_len])
    return errors / min_len