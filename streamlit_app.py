import streamlit as st
import pandas as pd
import os
import time
import threading
import plotly.express as px

DATA_DIR = "local_storage"
ttl_arquivos_maximo = 10 #horas
intervalo_checagem = 18000 #5 horas em segundos

os.makedirs(DATA_DIR, exist_ok=True)

def limpar_csvs_antigos():
    """Remove arquivos CSV da pasta especificada que tenham mais de 'horas' de existência."""
    while True:
        tempo_limite = time.time() - (ttl_arquivos_maximo * 3600)
        #teste 60 segundos
        #tempo_limite = time.time() - 60

        if os.path.exists(DATA_DIR):
            for arquivo in os.listdir(DATA_DIR):
                caminho_arquivo = os.path.join(DATA_DIR, arquivo)

                if arquivo.endswith(".csv") and os.path.isfile(caminho_arquivo):
                    tempo_modificacao = os.path.getmtime(caminho_arquivo)
                    
                    print(tempo_modificacao)
                    print(tempo_limite)

                    if tempo_modificacao < tempo_limite:
                        os.remove(caminho_arquivo)
                        
        time.sleep(intervalo_checagem)  # Aguarda antes de verificar novamente

# Inicia a limpeza automática em uma thread separada
def iniciar_limpador():
    thread = threading.Thread(target=limpar_csvs_antigos, daemon=True)
    thread.start()

# Iniciar a thread quando o Streamlit carregar
if "limpador_iniciado" not in st.session_state:
    iniciar_limpador()
    st.session_state.limpador_iniciado = True

def carregar_dados(aba_nome):
    print(aba_nome)
    file_path = os.path.join(DATA_DIR, f"{aba_nome}.csv")

    if os.path.exists(file_path):
        return pd.read_csv(file_path, index_col=False).iloc[: , 1:]
    
    return pd.DataFrame(columns=['I', 'II', 'III', 'IV'])

def salvar_dados(aba_nome, df):
    file_path = os.path.join(DATA_DIR, f"{aba_nome}.csv")
    df.to_csv(file_path)
    st.success(f"Dados de {aba_nome} salvos!")


# Função para calcular os totais e o coeficiente
def calcular_totais(df):
    df = df.apply(pd.to_numeric, errors='coerce').fillna(0)  # Converte valores para numérico
    total_i = df['I'].sum()
    total_ii = df['II'].sum()
    total_iii = df['III'].sum()
    total_iv = df['IV'].sum()
    total = total_i + total_ii + total_iii + total_iv
    coeficiente = (total + total_ii + 2 * total_iii + 3 * total_iv) / total if total != 0 else 0
    return total_i, total_ii, total_iii, total_iv, total, coeficiente

# Função para criar a tabela dinâmica padrão
def criar_tabela_dinamica():
    return pd.DataFrame(columns=['I', 'II', 'III', 'IV'])

# Função para exibir as tabelas e resultados dentro de uma aba
def exibir_aba(aba_nome):
    #st.subheader(f"Tabela Dinâmica - {aba_nome}")

    # Carregar os dados do arquivo ou da sessão
    if aba_nome not in st.session_state:
        st.session_state[aba_nome] = carregar_dados(aba_nome)

    # Layout responsivo com 2 colunas (ajuste de tamanho)
    col1, col2 = st.columns([3, 1], gap="large")
    
    with col1:
        #st.write("### Tabela de Dados")
        # Tabela dinâmica
        df = criar_tabela_dinamica()
        df_edit = st.data_editor(st.session_state[aba_nome], key=f"{aba_nome}_table", num_rows="dynamic", width=700, height=400)

        # Botão de salvar
        if st.button("Salvar Dados", key=f"salvar_{aba_nome}"):
            st.session_state[aba_nome] = df_edit
            salvar_dados(aba_nome, df_edit)


    # Calculando os totais
    total_i, total_ii, total_iii, total_iv, total, coeficiente = calcular_totais(df_edit)

    with col2:
        # Feedback visual na coluna de resultados
        st.write("### Resultados")
        st.metric("Total I", total_i)
        st.metric("Total II", total_ii)
        st.metric("Total III", total_iii)
        st.metric("Total IV", total_iv)
        st.metric("Total", total)
        st.metric("Coeficiente", round(coeficiente, 2))

    return total_i, total_ii, total_iii, total_iv, total, coeficiente

# Função para consolidar os resultados gerais
def consolidar_resultados(total_i1, total_ii1, total_iii1, total_iv1, 
                          total_i2, total_ii2, total_iii2, total_iv2, 
                          total_i3, total_ii3, total_iii3, total_iv3):
    total_geral_i = total_i1 + total_i2 + total_i3
    total_geral_ii = total_ii1 + total_ii2 + total_ii3
    total_geral_iii = total_iii1 + total_iii2 + total_iii3
    total_geral_iv = total_iv1 + total_iv2 + total_iv3
    total_geral = total_geral_i + total_geral_ii + total_geral_iii + total_geral_iv
    coeficiente_geral = (total_geral_i + 2 * total_geral_ii + 3 * total_geral_iii + 4 * total_geral_iv) / total_geral if total_geral != 0 else 0
    return total_geral_i, total_geral_ii, total_geral_iii, total_geral_iv, total_geral, coeficiente_geral

# Configuração do layout inicial do aplicativo

# Definir título e favicon
st.set_page_config(page_title="CUF", page_icon="🚀")

st.title("Contagem Unidades Foliculares")

# Dividindo as abas principais
tab1, tab2, tab3, tab4 = st.tabs(["Meio", "Direita", "Esquerda", "Resultados"])

# Variáveis globais para armazenar os valores de cada aba
total_meio_i, total_meio_ii, total_meio_iii, total_meio_iv, total_coef_meio = 0, 0, 0, 0, 0
total_direita_i, total_direita_ii, total_direita_iii, total_direita_iv, total_coef_direita = 0, 0, 0, 0, 0
total_esquerda_i, total_esquerda_ii, total_esquerda_iii, total_esquerda_iv, total_coef_esquerda = 0, 0, 0, 0, 0

# Aba "Meio" com sub abas "Meio I", "Meio II" e "Resultado Geral Meio"
with tab1:
    #st.subheader("Aba Meio")
    sub_tab1, sub_tab2, sub_tab3 = st.tabs(["Meio I", "Meio II", "Resultado Geral Meio"])
    
    with sub_tab1:
        #st.subheader("Sub Aba - Meio I")
        total_meio1_i, total_meio1_ii, total_meio1_iii, total_meio1_iv, _, coef_meio1 = exibir_aba("Meio I")
    
    with sub_tab2:
        #st.subheader("Sub Aba - Meio II")
        total_meio2_i, total_meio2_ii, total_meio2_iii, total_meio2_iv, _, coef_meio2 = exibir_aba("Meio II")
    
    with sub_tab3:
        st.subheader("Resultado Geral Meio")
        # Cálculo do total do Meio (Meio I + Meio II)
        total_meio_i = total_meio1_i + total_meio2_i
        total_meio_ii = total_meio1_ii + total_meio2_ii
        total_meio_iii = total_meio1_iii + total_meio2_iii
        total_meio_iv = total_meio1_iv + total_meio2_iv
        total_coef_meio = coef_meio1 + coef_meio2
        total_meio_consolidado = total_meio_i + total_meio_ii + total_meio_iii + total_meio_iv

        st.metric("Total I - Meio", total_meio_i)
        st.metric("Total II - Meio", total_meio_ii)
        st.metric("Total III - Meio", total_meio_iii)
        st.metric("Total IV - Meio", total_meio_iv)
        st.metric("Total Meio", total_meio_consolidado)
        st.metric("Coeficiente Meio", round(total_coef_meio, 2))

# Aba "Direita" com sub abas "Direita I", "Direita II" e "Resultado Geral Direita"
with tab2:
    #st.subheader("Aba Direita")
    sub_tab1, sub_tab2, sub_tab3 = st.tabs(["Direita I", "Direita II", "Resultado Geral Direita"])
    
    with sub_tab1:
        #st.subheader("Sub Aba - Direita I")
        total_direita1_i, total_direita1_ii, total_direita1_iii, total_direita1_iv, _, coef_direita1 = exibir_aba("Direita I")
    
    with sub_tab2:
        #st.subheader("Sub Aba - Direita II")
        total_direita2_i, total_direita2_ii, total_direita2_iii, total_direita2_iv, _, coef_direita2 = exibir_aba("Direita II")
    
    with sub_tab3:
        st.subheader("Resultado Geral Direita")
        # Cálculo do total da Direita (Direita I + Direita II)
        total_direita_i = total_direita1_i + total_direita2_i
        total_direita_ii = total_direita1_ii + total_direita2_ii
        total_direita_iii = total_direita1_iii + total_direita2_iii
        total_direita_iv = total_direita1_iv + total_direita2_iv
        total_coef_direita = coef_direita1 + coef_direita2
        total_direita_consolidado = total_direita_i + total_direita_ii + total_direita_iii + total_direita_iv

        st.metric("Total I - Direita", total_direita_i)
        st.metric("Total II - Direita", total_direita_ii)
        st.metric("Total III - Direita", total_direita_iii)
        st.metric("Total IV - Direita", total_direita_iv)
        st.metric("Total Direita", total_direita_consolidado)
        st.metric("Coeficiente Direita", round(total_coef_direita, 2))


# Aba "Esquerda" com sub abas "Esquerda I", "Esquerda II" e "Resultado Geral Esquerda"
with tab3:
    #st.subheader("Aba Esquerda")
    sub_tab1, sub_tab2, sub_tab3 = st.tabs(["Esquerda I", "Esquerda II", "Resultado Geral Esquerda"])
    
    with sub_tab1:
        #st.subheader("Sub Aba - Esquerda I")
        total_esquerda1_i, total_esquerda1_ii, total_esquerda1_iii, total_esquerda1_iv, _, coef_esquerda1 = exibir_aba("Esquerda I")
    
    with sub_tab2:
        #st.subheader("Sub Aba - Esquerda II")
        total_esquerda2_i, total_esquerda2_ii, total_esquerda2_iii, total_esquerda2_iv, _, coef_esquerda2 = exibir_aba("Esquerda II")
    
    with sub_tab3:
        st.subheader("Resultado Geral Esquerda")
        # Cálculo do total da Esquerda (Esquerda I + Esquerda II)
        total_esquerda_i = total_esquerda1_i + total_esquerda2_i
        total_esquerda_ii = total_esquerda1_ii + total_esquerda2_ii
        total_esquerda_iii = total_esquerda1_iii + total_esquerda2_iii
        total_esquerda_iv = total_esquerda1_iv + total_esquerda2_iv
        total_coef_esquerda = coef_esquerda1 + coef_esquerda2
        total_esquerda_consolidado = total_esquerda_i + total_esquerda_ii + total_esquerda_iii + total_esquerda_iv

        st.metric("Total I - Esquerda", total_esquerda_i)
        st.metric("Total II - Esquerda", total_esquerda_ii)
        st.metric("Total III - Esquerda", total_esquerda_iii)
        st.metric("Total IV - Esquerda", total_esquerda_iv)
        st.metric("Total Esquerda", total_esquerda_consolidado)
        st.metric("Coeficiente Esquerda", round(total_coef_esquerda, 2))

# Aba "Resultados" consolidada
with tab4:
    st.subheader("Resultados Gerais Consolidados")

    # Consolidando os totais
    total_geral_i, total_geral_ii, total_geral_iii, total_geral_iv, total_geral, coeficiente_geral = consolidar_resultados(
        total_meio_i, total_meio_ii, total_meio_iii, total_meio_iv,
        total_direita_i, total_direita_ii, total_direita_iii, total_direita_iv,
        total_esquerda_i, total_esquerda_ii, total_esquerda_iii, total_esquerda_iv
    )

    # Layout responsivo com 2 colunas (ajuste de tamanho)
    col1, col2 = st.columns([2, 2], gap="large")
    
    with col1:
        # Exibindo os resultados gerais
        st.metric("Total Geral I", total_geral_i)
        st.metric("Total Geral II", total_geral_ii)
        st.metric("Total Geral III", total_geral_iii)
        st.metric("Total Geral IV", total_geral_iv)
        st.metric("Total Consolidado", total_geral)
        st.metric("Coeficiente Geral", round(coeficiente_geral, 2))

    with col2:
        # Gráfico de Pizza
        df_pizza = pd.DataFrame({
            "Categoria": ["Total Geral I", "Total Geral II", "Total Geral III", "Total Geral IV"],
            "Total": [total_geral_i, total_geral_ii, total_geral_iii, total_geral_iv]
        })
        
        fig = px.pie(df_pizza, names='Categoria', values='Total')
        st.plotly_chart(fig)