import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import utils
import source_coding as src
import modulation as mod
import textwrap

# Configuração da Página
st.set_page_config(page_title="Simulador de Redes", layout="wide")

st.title("📡 Simulador de Transmissão Digital")
st.markdown("""
Este painel simula as camadas físicas de um sistema de comunicação.
Alterando os parâmetros à esquerda, você vê o impacto no sinal em tempo real.
""")

# --- SIDEBAR (Controles) ---
st.sidebar.header("Parâmetros do Canal")

# Input de Mensagem
mensagem = st.sidebar.text_input("Mensagem a enviar:", "Redes 2025")
if not mensagem:
    st.warning("Digite uma mensagem para começar.")
    st.stop()

# Controle de Ruído
snr_db = st.sidebar.slider("Relação Sinal-Ruído (SNR dB)", min_value=0, max_value=30, value=15)

# Escolha de Modulação
tipo_modulacao = st.sidebar.selectbox("Esquema de Modulação", ["BPSK", "16-QAM"])

# --- PROCESSAMENTO (Backend) ---

# 1. Fonte
bits_originais = utils.str_to_bits(mensagem)

# Função auxiliar de ruído (trazida para cá para facilitar o uso no slider)
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
    # Precisamos do tamanho original para cortar o padding
    bits_recuperados = mod.qam16_demodulate(rx_signal, len(bits_originais))

# 3. Pipeline de Codificação de Linha (Manchester) - Apenas para visualização de onda
tx_manch = src.manchester_encode(bits_originais)
# Pegamos apenas um trecho para o gráfico não ficar poluido
recorte_bits = 16 # Visualizar bits correspondentes a 2 letras
recorte_manch = tx_manch[:recorte_bits*2] 

# 4. Métricas
ber = utils.calculate_ber(bits_originais, bits_recuperados)
texto_recuperado = utils.bits_to_str(bits_recuperados)
sucesso = (ber == 0)

# --- VISUALIZAÇÃO (Frontend) ---

# Colunas para exibir dados brutos
col1, col2 = st.columns(2)

with col1:
    st.subheader("1. Transmissor (Tx)")
    st.text(f"Texto Original: {mensagem}")
    st.caption("Bits:")
    bit_string = "".join(map(str, bits_originais))
    wrapped_bits = textwrap.fill(bit_string, width=80)  # Ajuste o valor de width conforme necessário
    st.code(wrapped_bits, language="text", height=90)

with col2:
    st.subheader("4. Receptor (Rx)")
    st.text(f"Texto Decodificado: {texto_recuperado}")
    
    # Indicador de Sucesso visual
    if sucesso:
        st.success(f"Transmissão Perfeita! BER: {ber:.5f}")
    else:
        st.error(f"Erros Detectados! BER: {ber:.5f}")

st.divider()

# Gráficos
tab1, tab2 = st.tabs(["Diagrama de Constelação (IQ)", "Forma de Onda (Manchester)"])

with tab1:
    st.markdown(f"**Visualização da Modulação {tipo_modulacao}**")
    st.markdown("Os pontos azuis são o que chegou (com ruído). Os X vermelhos são os alvos ideais.")
    
    fig_const, ax = plt.subplots(figsize=(8, 4))
    
    # Plot dos pontos recebidos
    if tipo_modulacao == "BPSK":
        # BPSK é real, mas plotamos no plano complexo para padronizar
        ax.scatter(np.real(rx_signal), np.zeros_like(rx_signal), alpha=0.5, label='Recebido (Rx)')
        ax.scatter([1, -1], [0, 0], color='red', marker='x', s=100, label='Ideal (Tx)')
    else:
        # QAM
        ax.scatter(np.real(rx_signal), np.imag(rx_signal), alpha=0.5, label='Recebido (Rx)')
        # Pontos ideais do QAM
        ideais = list(mod.QAM_MAP.values())
        ideais_norm = np.array(ideais) / mod.NORM_FACTOR
        ax.scatter(np.real(ideais_norm), np.imag(ideais_norm), color='red', marker='x', s=100, label='Ideal (Tx)')
    
    ax.axhline(0, color='gray', linestyle='--')
    ax.axvline(0, color='gray', linestyle='--')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_title(f"Constelação {tipo_modulacao} com SNR={snr_db}dB")
    st.pyplot(fig_const)

with tab2:
    st.markdown("**Visualização do Código de Linha (Banda Base)**")
    st.markdown("Este é o sinal elétrico (Voltagem) representando os primeiros caracteres.")
    
    fig_wave, ax2 = plt.subplots(figsize=(10, 3))
    # Cria eixo de tempo
    t = np.arange(len(recorte_manch))
    
    # Plot estilo "Digital" (step)
    ax2.step(t, recorte_manch, where='post', color='green', linewidth=2)
    ax2.set_ylim(-1.5, 1.5)
    ax2.set_title("Sinal Manchester (Primeiros bits)")
    ax2.set_xlabel("Amostras (Tempo)")
    ax2.set_ylabel("Amplitude (Volts)")
    ax2.grid(True)
    
    st.pyplot(fig_wave)

# Debug Data Expander
with st.expander("Ver Detalhes Técnicos dos Arrays"):
    st.write("Vetor de Bits Original:", bits_originais)
    st.write("Sinal Modulado (Complexo/Real):", tx_signal)