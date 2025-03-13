# -*- coding: utf-8 -*-
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from PIL import Image
from io import BytesIO
import streamlit as st
import time

# A configuração da página deve ser a primeira coisa no código
st.set_page_config(page_title='Telemarketing analysis',
                   page_icon='telmarketing_icon.png',
                   layout='wide',
                   initial_sidebar_state='expanded')

# Configuração do tema do Seaborn
custom_params = {"axes.spines.right": False, "axes.spines.top": False}
sns.set_theme(style="ticks", rc=custom_params)

# Função para leitura dos dados
@st.cache_data(show_spinner=True)
def load_data(file_data):
    try:
        return pd.read_csv(file_data, sep=';')
    except:
        return pd.read_excel(file_data)

# Função para filtros com opção "ALL"
@st.cache_data(show_spinner=True)
def multiselect_filter(relatorio, col, selecionados):
    if 'all' in selecionados:
        return relatorio
    else:
        return relatorio[relatorio[col].isin(selecionados)].reset_index(drop=True)

# Função para converter DF para CSV
@st.cache_data
def df_toString(df):
    return df.to_csv(index=False).encode('utf-8')

# Função para converter DF para Excel
@st.cache_data
def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
        writer.close()
    return output.getvalue()

# Função principal do app
def main():
    st.title('Telemarketing analysis')
    st.markdown("---")

    # Apresenta uma imagem
    image = Image.open('Bank-Branding.jpg')
    st.sidebar.image(image)

    # Botão para carregar um arquivo no app
    st.sidebar.write("## Upload file")
    data_file_1 = st.sidebar.file_uploader("Bank marketing data", type=['csv', 'xlsx'])

    # Verificando se há conteúdo carregado no app
    if data_file_1 is not None:
        start = time.time()
        bank_raw = load_data(data_file_1)

        st.write('Time: ', time.time() - start)
        bank = bank_raw.copy()

        st.write('## Before filters')
        st.write(bank_raw.head())

        with st.sidebar.form(key='my_form'):
            graph_type = st.radio('Graph type: ', ('Bars', 'Pie'))

            # IDADES
            max_age = int(bank.age.max())
            min_age = int(bank.age.min())
            idades = st.slider('Age', min_age, max_age, (min_age, max_age), 1)

            # Filtros adicionais
            filters = {
                "Job": "job",
                "Marital status": "marital",
                "Default?": "default",
                "Housing?": "housing",
                "Any loan?": "loan",
                "Contact info": "contact",
                "Contact month": "month",
                "Days of the week": "day_of_week"
            }

            selected_filters = {}
            for label, col in filters.items():
                options = bank[col].unique().tolist() + ['all']
                selected_filters[col] = st.sidebar.multiselect(label, options, ['all'])

            # Aplicação dos filtros
            bank = bank.query("age >= @idades[0] and age <= @idades[1]")
            for col, selected in selected_filters.items():
                bank = multiselect_filter(bank, col, selected)

            submit_button = st.form_submit_button(label='Apply filters')

        # Botões de download dos dados filtrados
        st.write('## After filters')
        st.write(bank.head())

        csv = df_toString(bank)
        st.download_button(label="Download data as CSV",
                           data=csv,
                           file_name='bank-data-filtered.csv',
                           mime='text/csv')

        df_xlsx = to_excel(bank)
        st.download_button(label='Download data as Excel',
                           data=df_xlsx,
                           file_name='bank-data-filtered.xlsx')

        st.markdown("---")

        # Gráficos
        fig, ax = plt.subplots(1, 2, figsize=(5, 3))

        bank_raw_target_perc = bank_raw.y.value_counts(normalize=True).to_frame() * 100
        bank_raw_target_perc = bank_raw_target_perc.sort_index()

        try:
            bank_target_perc = bank.y.value_counts(normalize=True).to_frame() * 100
            bank_target_perc = bank_target_perc.sort_index()
        except:
            st.error('Filter error!')
            return

        col1, col2 = st.columns(2)

        df_xlsx = to_excel(bank_target_perc)
        col1.write('### Original data')
        col1.write(bank_raw_target_perc)
        col1.download_button(label='Download',
                             data=df_xlsx,
                             file_name='bank_raw_y.xlsx')

        df_xlsx = to_excel(bank_target_perc)
        col2.write('### Filtered data')
        col2.write(bank_target_perc)
        col2.download_button(label='Download',
                             data=df_xlsx,
                             file_name='bank_y.xlsx')

        st.markdown("---")

        # Plots
        if graph_type == 'Bars':
            sns.barplot(x=bank_raw_target_perc.index, y='Percentage', data=bank_raw_target_perc, ax=ax[0])
            sns.barplot(x=bank_target_perc.index, y='Percentage', data=bank_target_perc, ax=ax[1])
        else:
            bank_raw_target_perc.plot(kind='pie', y='Percentage', autopct='%.2f%%', ax=ax[0])
            bank_target_perc.plot(kind='pie', y='Percentage', autopct='%.2f%%', ax=ax[1])

        st.pyplot(fig)

# Executando o app
if __name__ == '__main__':
    main()
