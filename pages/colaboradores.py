import streamlit as st
import pandas as pd
import sqlite3
import datetime
import calendar

# Função para conectar ao banco de dados
def conectar_banco():
    return sqlite3.connect("vendas.db")

# Função para carregar os colaboradores do banco de dados
def carregar_colaboradores():
    conn = conectar_banco()
    df = pd.read_sql("SELECT codigo, colaborador, cod_nome_colab FROM colaboradores", conn)
    conn.close()
    return df

# Função para carregar as vendas gerais
def carregar_vendas():
    conn = conectar_banco()
    df = pd.read_sql("SELECT * FROM vendas_vendedores", conn)
    conn.close()
    return df

# Função para carregar vendas por grupo
def carregar_vendas_grupo(grupo):
    conn = conectar_banco()
    df = pd.read_sql(f"SELECT * FROM vendas_{grupo}", conn)
    conn.close()
    return df



# Função para análise individual do colaborador
def colab_individual():
    st.header('Análise Individual do Vendedor')

    # Carregar os dados
    df_colaboradores = carregar_colaboradores()
    df_vendas = carregar_vendas()
    df_vendas_genericos = carregar_vendas_grupo('genericos')
    df_vendas_similares = carregar_vendas_grupo('similares')
    df_vendas_perfumaria = carregar_vendas_grupo('perfumaria')
    df_vendas_csr_referencia = carregar_vendas_grupo('csr_referencia')
    df_vendas_csr_gensim = carregar_vendas_grupo('csr_gensim')
    lst_lideres = ['9','11','24','33','42','66','75','87','93']

    # Seleção do vendedors
    lst_vendedor = df_colaboradores['cod_nome_colab'].unique()
    seletor_colab = st.multiselect('Selecione o vendedor', lst_vendedor,default=[])
    if seletor_colab:
        lista_codigos_vendedores = [int(i.split('-')[0].strip()) for i in seletor_colab]

        # Seleção de período
        ano = int(st.selectbox("selecione o ano de vendas:", ['2025']))
        mes = st.selectbox("Selecione o mês de vendas:",
                    ['01 - Janeiro', '02 - Fevereiro', '03 - Março', '04 - Abril', '05 - Maio', '06 - Junho',
                    '07 - Julho', '08 - Agosto', '09 - Setembro', '10 - Outubro', '11 - Novembro', '12 - Dezembro'])
        mes = int(mes.split('-')[0])

        data_inicial = datetime.date(int(ano), int(mes), 1)

        # Determinar o último dia do mês
        ultimo_dia = calendar.monthrange(int(ano), mes)[1]
        data_final = datetime.date(int(ano), mes, ultimo_dia)

        
        # Converter a coluna 'data' para datetime antes de filtrar
        df_vendas['data'] = pd.to_datetime(df_vendas['data'])
        df_vendas_genericos['data'] = pd.to_datetime(df_vendas_genericos['data'], errors='coerce')
        df_vendas_similares['data'] = pd.to_datetime(df_vendas_similares['data'], errors='coerce')
        df_vendas_perfumaria['data'] = pd.to_datetime(df_vendas_perfumaria['data'], errors='coerce')
        df_vendas_csr_referencia['data'] = pd.to_datetime(df_vendas_csr_referencia['data'], errors='coerce')
        df_vendas_csr_gensim['data'] = pd.to_datetime(df_vendas_csr_gensim['data'], errors='coerce')

        # Filtrar vendas pelo vendedor e período
        df_vendedor = df_vendas.query("vendedor in @lista_codigos_vendedores and data >= @data_inicial and data <= @data_final")
        df_vendas_genericos = df_vendas_genericos.query("vendedor in @lista_codigos_vendedores and data >= @data_inicial and data <= @data_final")
        df_vendas_similares = df_vendas_similares.query("vendedor in @lista_codigos_vendedores and data >= @data_inicial and data <= @data_final")
        df_vendas_perfumaria = df_vendas_perfumaria.query("vendedor in @lista_codigos_vendedores and data >= @data_inicial and data <= @data_final")
        df_vendas_csr_referencia = df_vendas_csr_referencia.query("vendedor in @lista_codigos_vendedores and data >= @data_inicial and data <= @data_final")
        df_vendas_csr_gensim = df_vendas_csr_gensim.query("vendedor in @lista_codigos_vendedores and data >= @data_inicial and data <= @data_final")
    
        # KPIs individuais
        try:
            venda_liquida = round(df_vendedor['valor_liquido'].sum(), 2)
            clientes_atendidos = df_vendedor['cupom'].count()
            tkm = round(venda_liquida / clientes_atendidos, 2) if clientes_atendidos > 0 else 0
            valor_desconto = -df_vendedor['valor_desconto'].sum()
            venda_bruta = venda_liquida + valor_desconto
            desconto_percent = round(valor_desconto / venda_bruta * 100, 2) if venda_bruta > 0 else 0
            vendas_genericos_similares = round(df_vendas_genericos['valor_liquido'].sum() + df_vendas_similares['valor_liquido'].sum(), 2)
            vendas_perfumaria = round(df_vendas_perfumaria['valor_liquido'].sum(), 2)
            vendas_csr = round(df_vendas_csr_referencia['valor_liquido'].sum() + df_vendas_csr_gensim['valor_liquido'].sum(), 2)

            cupons_nao_identificados = df_vendedor['cliente'].isna().sum()
            cupons_identificados = df_vendedor['cliente'].count()
            cupons_identificados_percent = round(cupons_identificados/(cupons_identificados+cupons_nao_identificados)*100,2)
            df_ipc_bonificados = pd.read_excel('planilhas/vendas/vendedores/ipc.xls')
            df_ipc_bonificados = df_ipc_bonificados.query("codigo in @lista_codigos_vendedores")
            ipc = df_ipc_bonificados['ipc'].mean()
            bonificados_2_5reais = round(df_ipc_bonificados['bonificados_2.5reais'].sum() * 2.5,2)
            bonificados_5reais = round(df_ipc_bonificados['bonificados_5reais'].sum() * 5,2)
            bonificados_10reais = round(df_ipc_bonificados['bonificados_10reais'].sum() * 10,2)
            perfumaria_comissionada = round(df_ipc_bonificados['perfumaria_comissionada'].sum(),2)
            validade = round(df_ipc_bonificados['validade'].sum() * 0.05,2)

            kpi1, kpi2, kpi3 = st.columns(3)
            with kpi1:
                st.metric(label='Venda líquida', value=f'R$ {venda_liquida}')
                st.metric(label='% desconto concedido', value=f'{desconto_percent}%')
                st.metric(label='Vendas Genéricos/Similares', value=f'R$ {vendas_genericos_similares}')
            with kpi2:
                st.metric(label='Clientes atendidos', value=clientes_atendidos)
                st.metric(label='% cupons com clientes cadastrados', value=f'{cupons_identificados_percent}%')
                st.metric(label='Vendas Perfumaria', value=f'R$ {vendas_perfumaria}')
            with kpi3:
                st.metric(label='Ticket médio', value=f'R$ {tkm}')
                st.metric(label='Itens por cupom', value=ipc)
                st.metric(label='Vendas CSR', value=f'R$ {vendas_csr}')


        except Exception as e:
            st.warning(f'Erro ao calcular KPIs: {e}')
        
        st.subheader('Evolução das metas e comissões:')
        
        # meta ZERO
        if venda_liquida > 25000:
            meta_zero = round(vendas_genericos_similares*0.02,2)
            meta_zero_icon = f'R$ {meta_zero} ✅'
        else:
            meta_zero = 0
            meta_zero_icon = f'❌'
            
            
        # meta_1
        if (meta_zero>0) and (tkm > 50) and (ipc>0):
            meta_1 = round(100.00,2)
            meta_1_icon = f'R$ {meta_1} ✅'
        else:
            meta_1 = 0
            meta_1_icon = f'❌'
            
        # meta_2
        
        if (meta_zero>0):
            meta_2 = round(perfumaria_comissionada*0.02,2)
            meta_2_icon = f'R$ {meta_2} ✅'
        else:
            meta_2 = 0
            meta_2_icon = f'❌'
            
        # meta_3
        if (meta_zero>0) and (ipc >= 2.0):
            meta_3 = round(100.00,2)
            meta_3_icon = f'R$ {meta_3} ✅'
        else:
            meta_3 = 0
            meta_3_icon = f'❌'
            
        # meta_4
        if (meta_zero>0) and (vendas_perfumaria >= 10000):
            meta_4 = round(100.00,2)
            meta_4_icon = f'R$ {meta_4} ✅'
        else:
            meta_4 = 0
            meta_4_icon = f'❌'
            
        # meta_5
        if (meta_zero>0) and (venda_liquida > 35000):
            meta_5 = round(vendas_genericos_similares*0.01,2)
            meta_5_icon = f'R$ {meta_5} ✅'
        else:
            meta_5 = 0
            meta_5_icon = f'❌'

        # meta_6
        if (meta_zero>0) and (venda_liquida > 50000):
            meta_6 = round(vendas_genericos_similares*0.02,2)
            meta_6_icon = f'R$ {meta_6} ✅'
        else:
            meta_6 = 0
            meta_6_icon = f'❌'
            

        if bonificados_2_5reais > 0:
            bon_2_5reais_icon = f'R$ {bonificados_2_5reais} ✅'
        else:
            bon_2_5reais_icon = f'❌'

        if bonificados_5reais > 0:
            bon_5reais_icon = f'R$ {bonificados_5reais} ✅'
        else:
            bon_5reais_icon = f'❌'
            
        if bonificados_10reais > 0:
            bon_10reais_icon = f'R$ {bonificados_10reais} ✅'
        else:
            bon_10reais_icon = f'❌'

        if validade > 0:
            validade_icon = f'R$ {validade} ✅'
        else:
            validade_icon = f'❌'
            
        # KPI's de Metas atingidas
        col_meta_1,col_meta_2,col_meta_3 =  st.columns(3)
        with col_meta_1:
            st.metric(label='Meta ZERO - R$ 25.000,00', value=f'{meta_zero_icon}', help=f'Essa meta ativa as outras metas, se não atingir a meta ZERO, não tem direito as outras metas!')
            st.metric(label='Meta 3 - IPC', value= f'{meta_3_icon}', help=f'Itens por cliente acima de 2.00. O seu IPC foi de {ipc}')
            st.metric(label='Meta 6 - 50k', value= f'{meta_6_icon}', help=f'Venda total acima de 50.000,00 . Você vendeu {venda_liquida}')
            st.metric(label='Bonificados 2.5 reais', value=f'{bon_2_5reais_icon}')
            
        with col_meta_2:
            st.metric(label='Meta 1 - TKM', value= f'{meta_1_icon}', help=f'Ticket médio acima de 50,00. O seu TKM foi de {tkm}')
            st.metric(label='Meta 4 - Perfumaria', value= f'{meta_4_icon}', help=f'Venda de Perfumaria acima de 10.000,00. Você vendeu {vendas_perfumaria}')
            st.metric(label='Bonificados 5 reais', value=f'{bon_5reais_icon}')
            st.metric(label='Pré-vencidos', value=f'{validade_icon}')
            
        with col_meta_3:
            st.metric(label='Meta 2 - Comissão 2% em perfumaria comissionada', value= f'{meta_2_icon}', help=f'Você vendeu R$ {perfumaria_comissionada} em perfumaria comissionada (Dermos, perfumes e maquiagens)')
            st.metric(label='Meta 5 - 35k', value= f'{meta_5_icon}', help=f'Venda total acima de 35.000,00 . Você vendeu {venda_liquida}')
            st.metric(label='Bonificados 10 reais', value=f'{bon_10reais_icon}')

        premio_lider = 0
        if str(lista_codigos_vendedores[0]) in lst_lideres:
            meta = st.number_input('Qual a meta da loja?')
            venda = st.number_input('Qual foi a venda da loja?')
            if venda >= meta:
                premio_lider = venda * 0.5/100
                st.success(f"PARABÉNS você atingiu a meta da loja! Seu prêmio é de R$ {round(premio_lider,2)}")
            else:
                premio_lider = venda * 0.25/100
                st.warning(f"Infelizmente você não atingiu a meta da loja, sua premiação é de R$ {round(premio_lider,2)}")
                    
        
        if meta_zero > 0:
            meta_total = round(meta_zero+meta_1+meta_2+meta_3+meta_4+meta_5+meta_6+bonificados_10reais+bonificados_5reais+bonificados_2_5reais+validade+premio_lider,2)
            st.success(f'Sua Comissão referente as vendas do mês {data_inicial.month} é de R$ {meta_total}')
        else:
            meta_total = round(bonificados_10reais+bonificados_5reais+bonificados_2_5reais+validade+premio_lider,2)
            st.error(f'Infelizmente você não atingiu a META ZERO no mês {data_inicial.month}. Sua comissão é de {meta_total}')
    
    else:
        st.warning("Insira o vendedor!")

    


colab_individual()