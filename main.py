# main.py
import numpy as np
import matplotlib.pyplot as plt
from scipy.special import erfc # Necessário para a curva teórica
import utils
import source_coding as src
import modulation as mod

def add_awgn_noise(signal, snr_db):
    """
    Adiciona Ruído Branco Gaussiano Aditivo (AWGN) ao sinal.
    """
    sig_power = np.mean(np.abs(signal) ** 2)
    snr_linear = 10 ** (snr_db / 10)
    noise_power = sig_power / snr_linear
    
    if np.iscomplexobj(signal):
        noise = (np.random.normal(0, np.sqrt(noise_power/2), len(signal)) + 
                 1j * np.random.normal(0, np.sqrt(noise_power/2), len(signal)))
    else:
        noise = np.random.normal(0, np.sqrt(noise_power), len(signal))
        
    return signal + noise

def calculate_theoretical_ber(snr_db_range):
    """
    Calcula as curvas teóricas para comparação.
    Isso prova a coerência dos resultados (pedido do professor).
    """
    snr_linear = 10 ** (np.array(snr_db_range) / 10)
    
    # Teoria BPSK: 0.5 * erfc(sqrt(SNR))
    # Nota: SNR linear aqui é Eb/N0 para BPSK
    theoretical_bpsk = 0.5 * erfc(np.sqrt(snr_linear))
    
    # Teoria 16-QAM (Aproximação): 
    # Para M-QAM, Pb ~ (4/log2(M)) * Q(sqrt(3*log2(M)*SNR / (M-1)))
    # Simplificado para 16-QAM:
    theoretical_qam = 0.75 * erfc(np.sqrt(snr_linear * 4/10)) # Ajuste para energia média
    
    return theoretical_bpsk, theoretical_qam

def main():
    # 1. Configuração da Simulação Científica
    # Em vez de texto, usamos bits aleatórios para ter estatística robusta
    NUM_BITS = 100000  # 100 mil bits por ponto de SNR garante curvas suaves
    print(f"Iniciando simulação Monte Carlo com {NUM_BITS} bits por ciclo...")
    
    bits_originais = np.random.randint(0, 2, NUM_BITS)
    
    # Aumentamos o range para ver a queda do QAM (até 20dB igual a imagem de referência)
    snr_range = range(0, 21, 1) 
    
    ber_bpsk = []
    ber_qam = []
    ber_manchester = []

    # 2. Loop de Simulação
    for snr in snr_range:
        # --- BPSK Pipeline ---
        tx_bpsk = mod.bpsk_modulate(bits_originais)
        rx_bpsk_noise = add_awgn_noise(tx_bpsk, snr)
        rx_bits_bpsk = mod.bpsk_demodulate(rx_bpsk_noise)
        ber_bpsk.append(utils.calculate_ber(bits_originais, rx_bits_bpsk))

        # --- 16-QAM Pipeline ---
        tx_qam = mod.qam16_modulate(bits_originais)
        rx_qam_noise = add_awgn_noise(tx_qam, snr)
        rx_bits_qam = mod.qam16_demodulate(rx_qam_noise, len(bits_originais))
        ber_qam.append(utils.calculate_ber(bits_originais, rx_bits_qam))

        # --- Manchester (Banda Base) ---
        tx_manch = src.manchester_encode(bits_originais)
        rx_manch_noise = add_awgn_noise(tx_manch, snr)
        rx_bits_manch = src.manchester_decode(rx_manch_noise)
        ber_manchester.append(utils.calculate_ber(bits_originais, rx_bits_manch))

        print(f"SNR: {snr}dB | BER BPSK: {ber_bpsk[-1]:.5f} | BER QAM: {ber_qam[-1]:.5f}")

    # 3. Cálculo Teórico (Para desenhar as linhas sólidas de referência)
    theo_bpsk, theo_qam = calculate_theoretical_ber(snr_range)

    # 4. Plotagem Estilo "Paper Acadêmico" (Igual a referência)
    plt.figure(figsize=(10, 7))
    
    # Curvas Simuladas (Marcadores)
    plt.semilogy(snr_range, ber_bpsk, 'bo', label='BPSK (Simulado)', markersize=8, fillstyle='none')
    plt.semilogy(snr_range, ber_qam, 'rs', label='16-QAM (Simulado)', markersize=8, fillstyle='none')
    plt.semilogy(snr_range, ber_manchester, 'g^', label='Manchester (Simulado)', markersize=8, fillstyle='none')

    # Curvas Teóricas (Linhas Sólidas) - Prova a coerência
    plt.semilogy(snr_range, theo_bpsk, 'b-', linewidth=1, alpha=0.5, label='BPSK (Teórico)')
    plt.semilogy(snr_range, theo_qam, 'r-', linewidth=1, alpha=0.5, label='16-QAM (Teórico)')

    # Estilização
    plt.title('Comparação de BER vs SNR (Simulação vs Teoria)')
    plt.xlabel('SNR (dB)')
    plt.ylabel('Bit Error Rate (BER)')
    
    # Grid igual ao da referência (Maior e Menor)
    plt.grid(True, which="major", linestyle='-', linewidth=0.8)
    plt.grid(True, which="minor", linestyle=':', linewidth=0.5)
    
    plt.legend()
    
    # Limites para garantir a visualização "Waterfall"
    plt.ylim(0.00001, 1.2) 
    plt.xlim(0, 20)
    
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()