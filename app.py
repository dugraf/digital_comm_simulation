import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from scipy.special import erfc
import utils
import source_coding as src
import modulation as mod
import textwrap

# Configuração da Página
st.set_page_config(page_title="Simulador de Redes", layout="wide")

st.title("📡 Simulador de Transmissão Digital")
st.markdown("""
Este painel simula as camadas físicas. Ajuste o SNR para ver o impacto na Constelação e na Taxa de Erro (BER).
""")

# --- SIDEBAR (Controles) ---
st.sidebar.header("Parâmetros do Canal")

mensagem = st.sidebar.text_input("Mensagem a enviar:", "Redes de Computadores 2025")
if not mensagem:
    st.warning("Digite uma mensagem para começar.")
    st.stop()

# Controle de Ruído
snr_db = st.sidebar.slider("Relação Sinal-Ruído (SNR dB)", min_value=0, max_value=25, value=10)

# Escolha de Modulação
tipo_modulacao = st.sidebar.selectbox("Esquema de Modulação", ["BPSK", "16-QAM"])

# --- PROCESSAMENTO (Backend) ---

# 1. Fonte
bits_originais = utils.str_to_bits(mensagem)

# Função auxiliar de ruído
def add_noise(signal, snr):
    sig_power = np.mean(np.abs(signal) ** 2)
    snr_linear = 10 ** (snr / 10)
    noise_power = sig_power / snr_linear
    if np.iscomplexobj(signal):
        noise = (np.random.normal(0, np.sqrt(noise_power/2), len(signal)) + 
                 1j * np.random.normal(0, np.sqrt(noise_power/2), len(signal)))
    else:
        noise = np.random.normal(0, np.sqrt(noise_power), len(signal))
    return signal + noise

# 2. Pipeline de Modulação
tx_signal = None
rx_signal = None
bits_recuperados = None

if tipo_modulacao == "BPSK":
    tx_signal = mod.bpsk_modulate(bits_originais)
    rx_signal = add_noise(tx_signal, snr_db)
    bits_recuperados = mod.bpsk_demodulate(rx_signal)
elif tipo_modulacao == "16-QAM":
    tx_signal = mod.qam16_modulate(bits_originais)
    rx_signal = add_noise(tx_signal, snr_db)
    bits_recuperados = mod.qam16_demodulate(rx_signal, len(bits_originais))

# 3. Métricas
ber = utils.calculate_ber(bits_originais, bits_recuperados)
texto_recuperado = utils.bits_to_str(bits_recuperados)
sucesso = (ber == 0)

# --- VISUALIZAÇÃO (Frontend) ---

col1, col2 = st.columns(2)

with col1:
    st.subheader("1. Transmissor (Tx)")
    st.caption(f"Mensagem ({len(bits_originais)} bits):")
    st.text(mensagem)
    # Mostra apenas um pedaço dos bits para não poluir
    bit_string = "".join(map(str, bits_originais))
    wrapped_bits = textwrap.fill(bit_string, width=80)  # Ajuste o valor de width conforme necessário
    st.code(wrapped_bits, language="text", height=90)

with col2:
    st.subheader("4. Receptor (Rx)")
    st.caption("Mensagem Decodificada:")
    st.text(texto_recuperado)
    
    if sucesso:
        st.success(f"BER: {ber:.5f} (Sem erros)")
    else:
        st.error(f"BER: {ber:.5f} ({int(ber * len(bits_originais))} bits errados)")

st.divider()

# Abas Gráficas
tab1, tab2, tab3 = st.tabs(["Diagrama de Constelação", "Curva BER vs SNR (Comparativo)", "Sinal no Tempo"])

# --- ABA 1: CONSTELAÇÃO ---
with tab1:
    st.markdown(f"**Visualização: {tipo_modulacao} @ SNR {snr_db}dB**")
    
    fig_const, ax = plt.subplots(figsize=(6, 4))
    
    if tipo_modulacao == "BPSK":
        ax.scatter(np.real(rx_signal), np.zeros_like(rx_signal), alpha=0.5, label='Rx (Ruidoso)')
        ax.scatter([1, -1], [0, 0], color='red', marker='x', s=100, label='Tx (Ideal)')
    else:
        ax.scatter(np.real(rx_signal), np.imag(rx_signal), alpha=0.5, label='Rx (Ruidoso)')
        ideais = list(mod.QAM_MAP.values())
        ideais_norm = np.array(ideais) / mod.NORM_FACTOR
        ax.scatter(np.real(ideais_norm), np.imag(ideais_norm), color='red', marker='x', s=100, label='Tx (Ideal)')
    
    ax.axhline(0, color='gray', linestyle='--', alpha=0.5)
    ax.axvline(0, color='gray', linestyle='--', alpha=0.5)
    ax.legend(loc='upper right')
    ax.grid(True, alpha=0.3)
    ax.set_title(f"Dispersão da Constelação")
    ax.set_xlabel('Fase do sinal')
    st.pyplot(fig_const)

# --- ABA 2: CURVA BER (NOVO) ---
with tab3:
    st.markdown("**Sinal Manchester (Primeiros 32 bits)**")
    tx_manch = src.manchester_encode(bits_originais[:16]) # Pega primeiros 16 bits originais (vira 32 chips)
    
    fig_wave, ax2 = plt.subplots(figsize=(10, 2))
    t = np.arange(len(tx_manch))
    ax2.step(t, tx_manch, where='post', color='green', linewidth=1.5)
    ax2.set_ylim(-1.5, 1.5)
    ax2.set_xlabel("Amostras")
    ax2.set_ylabel("Volts")
    ax2.grid(True, alpha=0.3)
    st.pyplot(fig_wave)

# --- ABA 3: CURVA TEÓRICA + PONTO REAL (A PEDIDO DO USUÁRIO) ---
with tab2:
    st.markdown("Comparativo do desempenho atual vs Teoria Matemática.")
    
    # 1. Gerar dados teóricos (Background fixo)
    snr_axis = np.linspace(0, 25, 100)
    snr_linear_axis = 10 ** (snr_axis / 10)
    
    # Fórmulas Teóricas
    theo_bpsk = 0.5 * erfc(np.sqrt(snr_linear_axis))
    theo_qam = 0.75 * erfc(np.sqrt(0.4 * snr_linear_axis))
    
    fig_ber, ax_ber = plt.subplots(figsize=(8, 5))
    
    # Plota Linhas Teóricas
    ax_ber.semilogy(snr_axis, theo_bpsk, 'b--', alpha=0.3, label='Teórico BPSK')
    ax_ber.semilogy(snr_axis, theo_qam, 'r--', alpha=0.3, label='Teórico 16-QAM')
    
    # Plota o Ponto da Simulação Atual
    # Se BER for 0, log scale quebra. Então definimos um piso visual (10^-6)
    ber_plot = ber if ber > 0 else 1e-6
    
    cor_ponto = 'blue' if tipo_modulacao == 'BPSK' else 'red'
    label_ponto = f'Sua Simulação ({tipo_modulacao})'
    
    ax_ber.semilogy(snr_db, ber_plot, color=cor_ponto, marker='o', markersize=12, label=label_ponto)
    
    # Highlight se BER for zero
    if ber == 0:
        ax_ber.text(snr_db, 1.5e-6, "BER=0 (Perfeito)", color=cor_ponto, ha='center', fontweight='bold')

    ax_ber.set_xlabel('SNR (dB)')
    ax_ber.set_ylabel('BER (Bit Error Rate)')
    ax_ber.set_ylim(1e-6, 1)
    ax_ber.set_xlim(0, 25)
    ax_ber.grid(True, which="both", alpha=0.2)
    ax_ber.legend()
    ax_ber.set_title("Quão confiável é a minha transmissão com o nível de ruído atual?")
    
    st.pyplot(fig_ber)