import streamlit as st
import pandas as pd
from arquivados.function import analise_estoque, analise_estoque_grupo


def layout_compras():
    filial = st.selectbox('Escolha a filial:', ['001 - Matriz','004 - Centrinho','005 - Calil','007 - Rio Vermelho','008 - Vargem','009 - Canasvieiras','010 - Upa','011 - Trindade','012 - Palhoça','100 - Central'])
    cod_filial = filial[0:3]
    
    valor_em_estoque, valor_faltas, df_estoque = analise_estoque(cod_filial)
    
    valor_estoque_base = valor_em_estoque+valor_faltas

    st.subheader('Indicador de ruptura')
    kpi1,kpi2,kpi3 =  st.columns(3)
    with kpi1:
        st.metric(label='Ruptura total', value=f'{(valor_faltas/valor_estoque_base*100):.1f}%')
    with kpi2:
        st.metric(label='Valor em estoque', value=f'R$ {(valor_em_estoque/1000):.1f} mil')
    with kpi3:
        st.metric(label='Valor em faltas', value=f'R$ {(valor_faltas/1000):.1f} mil')
    
    with st.expander('Comprar Produtos', expanded=False):
        
        grupo_produtos = st.selectbox('Selecione o grupo de produtos e aguarde a geração da análise de ruptura',['Genéricos e Similares (por princípio ativo)','3000 - Éticos','8000 - Perfumaria', '9000 - Correlatos', '10000 - Conveniência'])
        st.write(grupo_produtos)
        
        kpi1,kpi2,kpi3 =  st.columns(3)
        

        if grupo_produtos == '3000 - Éticos':
            estoque_grupo, faltas_grupo, df_faltas_grupo, df_excesso_grupo = analise_estoque_grupo(df_estoque, grupo='3000')
            estoque_base_grupo = estoque_grupo+faltas_grupo
            
        elif grupo_produtos == '8000 - Perfumaria':
            estoque_grupo, faltas_grupo, df_faltas_grupo, df_excesso_grupo = analise_estoque_grupo(df_estoque, grupo='8000')
            estoque_base_grupo = estoque_grupo+faltas_grupo

        elif grupo_produtos == '9000 - Correlatos':
            estoque_grupo, faltas_grupo, df_faltas_grupo, df_excesso_grupo = analise_estoque_grupo(df_estoque, grupo='9000')
            estoque_base_grupo = estoque_grupo+faltas_grupo

        elif grupo_produtos == '10000 - Conveniência':
            estoque_grupo, faltas_grupo, df_faltas_grupo, df_excesso_grupo = analise_estoque_grupo(df_estoque, grupo='10000')
            estoque_base_grupo = estoque_grupo+faltas_grupo
            
        elif grupo_produtos == 'Genéricos e Similares (por princípio ativo)':
            estoque_grupo, faltas_grupo, df_faltas_grupo, df_excesso_grupo = analise_estoque_grupo(df_estoque, grupo='2000')
            estoque_base_grupo = estoque_grupo+faltas_grupo

            st.warning('Ainda estamos trabalhando nisso! Aguarde!')
            
        else:
            estoque_grupo = 1
            faltas_grupo = 1
            df_faltas_grupo = 1
            df_excesso_grupo = 1
            estoque_base_grupo = 1
            
        with kpi1:
            st.metric(label='Ruptura do grupo', value=f'{(faltas_grupo/estoque_base_grupo*100):.1f}%')
        with kpi2:
            st.metric(label='R$ estoque do grupo', value=f'R$ {(estoque_grupo/1000):.1f} mil')
        with kpi3:
            st.metric(label='R$ faltas do grupo', value=f'R$ {(faltas_grupo/1000):.1f} mil')
            
        ver_df_faltas_grupo = st.checkbox('Ver dataframe')
        if ver_df_faltas_grupo:
            st.write(df_faltas_grupo)
            
            
        #filtros avançados
        
        #comprar somente zerados
        filtro_avançado = st.selectbox('Selecione o filtro avançado', [
            'Nenhum filtro avançado',
            'Comprar por laboratório',
            ])
        #comprar por curva
        curvas = st.multiselect('Selecione as curvas',['A','B','C','D'])
        #comprar somente zerados
        somente_zerados = st.checkbox('somente zerados')
        
        
        

    with st.expander('Análise de Excesso de estoque', expanded=False):
        st.subheader('Indicador de Excesso de estoque')
        df_excesso_grupo['preco_custo'] = pd.to_numeric(df_excesso_grupo['preco_custo'], errors='coerce')
        df_excesso_grupo['valor_excesso'] = df_excesso_grupo['preco_custo']*df_excesso_grupo['excesso']
        excesso = df_excesso_grupo['valor_excesso'].sum()
        itens_excesso = df_excesso_grupo['excesso'].sum()
        
        kpi1,kpi2,kpi3 =  st.columns(3)
        with kpi1:
            st.metric(label='% de excesso no grupo', value=f'{(excesso/estoque_base_grupo*100):.1f}%')
        with kpi2:
            st.metric(label='R$ excesso do grupo', value=f'R$ {(excesso/1000):.1f} mil')
        with kpi3:
            st.metric(label='Qtd itens em excesso do grupo', value=f'{itens_excesso}')
        st.subheader('Produtos com estoque em excesso (estoque > demanda)')
        st.write(df_excesso_grupo)
    
    with st.expander('Análise de vendas perdidas', expanded=False):
        st.subheader('Vendas Perdidas')
        st.warning('Ainda estamos trabalhando nisso! Aguarde!')
        vendas_perdidas = 1300.00
        #st.write('Aqui vem o gráfico de valor em vendas perdidas no mês por dia..')
        #st.error(f'Até o momento foi registrado R$ {(vendas_perdidas):.2f} em vendas perdidas nesse mês!')