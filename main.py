# main.py
import numpy as np
import matplotlib.pyplot as plt
import utils
import source_coding as src
import modulation as mod

def add_awgn_noise(signal, snr_db):
    """
    Adiciona Ruído Branco Gaussiano Aditivo (AWGN) ao sinal.
    """
    # Calcula potência do sinal
    sig_power = np.mean(np.abs(signal) ** 2)
    
    # Converte SNR dB para linear: SNR = 10^(dB/10)
    snr_linear = 10 ** (snr_db / 10)
    
    # Calcula potência do ruído necessária
    noise_power = sig_power / snr_linear
    
    # Gera ruído complexo se o sinal for complexo, senão real
    if np.iscomplexobj(signal):
        noise = (np.random.normal(0, np.sqrt(noise_power/2), len(signal)) + 
                 1j * np.random.normal(0, np.sqrt(noise_power/2), len(signal)))
    else:
        noise = np.random.normal(0, np.sqrt(noise_power), len(signal))
        
    return signal + noise

def main():
    # 1. Configuração da Simulação
    # Usamos uma mensagem longa para ter estatística de erro confiável
    mensagem = input("Digite a mensagem que deseja enviar: ")
    bits_originais = utils.str_to_bits(mensagem)
    print(f"Enviando {len(bits_originais)} bits...")

    snr_range = range(0, 16, 1) # Testa de 0dB a 15dB
    ber_bpsk = []
    ber_qam = []
    ber_manchester = []

    # 2. Loop de Simulação (Monte Carlo)
    for snr in snr_range:
        # --- BPSK Pipeline ---
        tx_bpsk = mod.bpsk_modulate(bits_originais)           # Modula
        rx_bpsk_noise = add_awgn_noise(tx_bpsk, snr)          # Canal
        rx_bits_bpsk = mod.bpsk_demodulate(rx_bpsk_noise)     # Demodula
        ber_bpsk.append(utils.calculate_ber(bits_originais, rx_bits_bpsk))

        # --- 16-QAM Pipeline ---
        tx_qam = mod.qam16_modulate(bits_originais)
        rx_qam_noise = add_awgn_noise(tx_qam, snr)
        rx_bits_qam = mod.qam16_demodulate(rx_qam_noise, len(bits_originais))
        ber_qam.append(utils.calculate_ber(bits_originais, rx_bits_qam))

        # --- Manchester Pipeline (Simulando Transmissão em Banda Base Ruidosa) ---
        # Nota: Manchester consome mais largura de banda, testamos aqui como se fosse transmitido direto
        tx_manch = src.manchester_encode(bits_originais)
        rx_manch_noise = add_awgn_noise(tx_manch, snr)
        rx_bits_manch = src.manchester_decode(rx_manch_noise)
        ber_manchester.append(utils.calculate_ber(bits_originais, rx_bits_manch))

        print(f"SNR: {snr}dB | BER BPSK: {ber_bpsk[-1]:.5f} | BER QAM: {ber_qam[-1]:.5f}")

    # 3. Plotagem dos Resultados
    plt.figure(figsize=(10, 6))
    plt.semilogy(snr_range, ber_bpsk, 'b-o', label='BPSK')
    plt.semilogy(snr_range, ber_qam, 'r-s', label='16-QAM')
    plt.semilogy(snr_range, ber_manchester, 'g--', label='Manchester (Baseband)')
    
    plt.title('Performance BER vs SNR')
    plt.xlabel('SNR (dB)')
    plt.ylabel('Bit Error Rate (BER)')
    plt.grid(True, which="both", ls="-")
    plt.legend()
    plt.ylim(0.00001, 1) # Limita eixo Y para visualização limpa
    plt.show()

    # 4. Teste de recuperação de texto (com SNR alto para garantir sucesso)
    print("\n--- Teste de Recuperação (SNR=20dB) ---")
    tx_final = mod.qam16_modulate(utils.str_to_bits("Teste Final"))
    rx_final = add_awgn_noise(tx_final, 20)
    bits_recuperados = mod.qam16_demodulate(rx_final, len(utils.str_to_bits("Teste Final")))
    print(f"Texto Recuperado: {utils.bits_to_str(bits_recuperados)}")

if __name__ == "__main__":
    main()