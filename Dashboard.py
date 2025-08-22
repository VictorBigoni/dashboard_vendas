## --- Importando as bibliotecas ---
import streamlit as st
import requests
import pandas as pd
import plotly.express as px

# Definindo o streamlit para widemode como padrão
st.set_page_config(layout = 'wide')

# Função para formatar os valores monetários e de venda
def formata_numero(valor, prefixo = ''):
  for unidade in ['', 'mil']:
    if valor < 1000:
      return f'{prefixo} {valor:.2f} {unidade}'
    valor /= 1000
  return f'{prefixo} {valor:.2f} milhões'

# Adicionando título ao aplicativo
st.title('DASHBOARD DE VENDAS 🛒')

# Lendo dados da API
url = 'https://labdados.com/produtos'
regioes = ['Brasil', 'Centro-Oeste', 'Nordeste' , 'Norte', 'Sudeste', 'Sul']

# --- Barra lateral ---
# Título da barra lateral 
st.sidebar.title('Filtros 🔍')

# Criando filtro para regiões do Brasil
regiao = st.sidebar.selectbox('Região', regioes)

if regiao == 'Brasil':
  regiao = ''

# Criando filtro de anos
todos_anos = st.sidebar.checkbox('Dados de todo o período', value = True)

if todos_anos:
  ano = ''
else:
  ano = st.sidebar.slider('Ano', 2020, 2023)

query_string = {'regiao':regiao.lower(), 'ano':ano}

response = requests.get(url, params = query_string)
dados = pd.DataFrame.from_dict(response.json())

# Alterando formato da coluna de datas para datetime
dados['Data da Compra'] = pd.to_datetime(dados['Data da Compra'], format = '%d/%m/%Y')

# Criando o filtro dos vendedores
filtro_vendedores = st.sidebar.multiselect('Vendedores', dados['Vendedor'].unique())
if filtro_vendedores:
  dados = dados[dados['Vendedor'].isin(filtro_vendedores)]

## --- Tabelas ---
## --- Tabelas aba 1 ---
# Criando uma tabela com nome do Estado, latitude e longitude, além de um merge
# dessa tabela com a tabela agrupada da quantidade de receita de cada Estado.
receita_estados = dados.groupby('Local da compra')[['Preço']].sum()
receita_estados = dados.drop_duplicates(subset='Local da compra')[['Local da compra', 'lat', 'lon']].merge(receita_estados, left_on="Local da compra", right_index=True).sort_values('Preço', ascending=False)

# Criando tabela com agrupamento por mês
receita_mensal = dados.set_index('Data da Compra').groupby(pd.Grouper(freq='ME'))['Preço'].sum().reset_index()
receita_mensal['Ano'] = receita_mensal['Data da Compra'].dt.year
receita_mensal['Mes'] = receita_mensal['Data da Compra'].dt.month_name()

# Criando tabela de receita por categoria de produto
receita_categorias = dados.groupby('Categoria do Produto')[['Preço']].sum().sort_values('Preço', ascending=False)

## --- Tabelas aba 2 ---
# Criando tabela de vendas por Estado
vendas_estado = dados.groupby('Local da compra')[['Produto']].count()
vendas_estado = dados.drop_duplicates(subset='Local da compra')[['Local da compra', 'lat', 'lon']].merge(vendas_estado, left_on='Local da compra', right_index=True).sort_values('Produto', ascending=False)

# Criando tabela de vendas por mês
vendas_mensais = dados.set_index('Data da Compra').groupby(pd.Grouper(freq='ME'))[['Produto']].count().reset_index()
vendas_mensais['Ano'] = vendas_mensais['Data da Compra'].dt.year
vendas_mensais['Mes'] = vendas_mensais['Data da Compra'].dt.month_name()

#Criando tabela de quantidade de vendas por categoria de produto
vendas_categoria = dados.groupby('Categoria do Produto')[['Produto']].count().sort_values('Produto', ascending=False)

## --- Tabelas aba 3 ---
# Criando a tabela de vendedores
vendedores = pd.DataFrame(dados.groupby('Vendedor')['Preço'].agg(['sum', 'count']))

## --- Gráficos ---
# Gráfico de mapa mostrando a venda por estado
fig_mapa_receita = px.scatter_geo(receita_estados,
                                  lat = 'lat',
                                  lon = 'lon',
                                  scope = 'south america',
                                  size = 'Preço',
                                  template = 'seaborn',
                                  hover_name = 'Local da compra', 
                                  hover_data = {'lat':False, 'lon':False},
                                  title = 'Receita por Estado')

# Gráfico de linhas mostrando a receita mensal
fig_receita_mensal = px.line(receita_mensal,
                             x = 'Mes',
                             y = 'Preço',
                            markers = True,
                            range_y = (0, receita_mensal.max()),
                            color = 'Ano',
                            line_dash = 'Ano',
                            title = 'Receita mensal')

fig_receita_mensal.update_layout(yaxis_title = 'Receita')

 #Gráfico de barras com receita por estados
fig_receita_estados = px.bar(receita_estados.head(),
                             x = 'Local da compra',
                             y = 'Preço',
                             text_auto = True,
                             title = 'Top Estados (receita)')

fig_receita_estados.update_layout(yaxis_title = 'Receita')

# Gráfico de barras com receita por categoria de produto
fig_receita_categoria = px.bar(receita_categorias,
                               text_auto = True,
                               title = 'Receita por categoria')

fig_receita_categoria.update_layout(yaxis_title = 'Receita')

# Gráfico de mapa mostrando a quantidade de vendas por Estado
fig_mapa_vendas = px.scatter_geo(vendas_estado,
                                 lat = 'lat',
                                 lon = 'lon',
                                 scope = 'south america',
                                 size = 'Produto',
                                 template = 'seaborn',
                                 hover_name = 'Local da compra',
                                hover_data = {'lat':False, 'lon':False},
                                title = 'Quantidade de vendas por Estado')

# Gráfico de linhas com as vendas mensais
fig_vendas_mensais = px.line(vendas_mensais,
                             x = 'Mes',
                             y = 'Produto',
                             markers = True,
                             range_y = (0, vendas_mensais.max()),
                             color = 'Ano',
                             line_dash = 'Ano',
                             title = 'Vendas por mês')

fig_vendas_mensais.update_layout(yaxis_title = 'Produtos vendidos', xaxis_title = 'Mês')

 #Gráfico de barras com receita por estados
fig_vendas_estados = px.bar(vendas_estado.head(),
                             x = 'Local da compra',
                             y = 'Produto',
                             text_auto = True,
                             title = 'Top Estados (Vendas de produtos)')

fig_vendas_estados.update_layout(yaxis_title = 'Produtos vendidos', xaxis_title = '')

# Gráfico de barras com quantidade de vendas por categorias
fig_vendas_categoria = px.bar(vendas_categoria,
                              text_auto = True,
                              title = 'Quantidade de vendas por categoria')

fig_vendas_categoria.update_layout(yaxis_title = 'Produtos vendidos', xaxis=dict(showticklabels=False, title = ''))

## --- Visualização no Streamlit ---

# Construindo as abas
aba1, aba2, aba3 = st.tabs(['Receita', 'Quantidade de vendas', 'Vendedores'])

with aba1:
  # Definindo as colunas e colocando as primeiras métricas 
  coluna1, coluna2 = st.columns(2) 
  with coluna1:
    st.metric('Receita', formata_numero(dados['Preço'].sum(), 'R$'))
    st.plotly_chart(fig_mapa_receita, use_container_width=True)
    st.plotly_chart(fig_receita_estados, use_container_width=True)
  with coluna2:
    st.metric('Quantidade de vendas', formata_numero(dados.shape[0]))
    st.plotly_chart(fig_receita_mensal, use_container_width=True)
    st.plotly_chart(fig_receita_categoria, use_container_width=True)

with aba2:
  # Definindo as colunas e colocando as primeiras métricas 
  coluna1, coluna2 = st.columns(2) 
  with coluna1:
    st.metric('Receita', formata_numero(dados['Preço'].sum(), 'R$'))
    st.plotly_chart(fig_mapa_vendas,use_container_width=True)
    st.plotly_chart(fig_vendas_estados, use_container_width=True)
  with coluna2:
    st.metric('Quantidade de vendas', formata_numero(dados.shape[0]))
    st.plotly_chart(fig_vendas_mensais, use_container_width=True)
    st.plotly_chart(fig_vendas_categoria, use_container_width=True)

with aba3:
  qtd_vendedores = st.number_input('Quantidade de vendedores', 2, 10, 5)
  # Definindo as colunas e colocando as primeiras métricas 
  coluna1, coluna2 = st.columns(2) 
  with coluna1:
    st.metric('Receita', formata_numero(dados['Preço'].sum(), 'R$'))
    
    # Criando gráfico de receita total por vendedor
    fig_receita_vendedores = px.bar(vendedores[['sum']].sort_values('sum', ascending=False).head(qtd_vendedores),
                                    x = 'sum',
                                    y = vendedores[['sum']].sort_values('sum', ascending=False).head(qtd_vendedores).index,
                                    text_auto = True,
                                    title = f'Top {qtd_vendedores} vendedores (receita)')
    fig_receita_vendedores.update_layout(yaxis_title = '', xaxis_title = 'Valor em Reais')
    st.plotly_chart(fig_receita_vendedores, use_container_width=True)
  with coluna2:
    st.metric('Quantidade de vendas', formata_numero(dados.shape[0]))
    fig_vendas_vendedores = px.bar(vendedores[['count']].sort_values('count', ascending=False).head(qtd_vendedores),
                                    x = 'count',
                                    y = vendedores[['count']].sort_values('count', ascending=False).head(qtd_vendedores).index,
                                    text_auto = True,
                                    title = f'Top {qtd_vendedores} vendedores (quantidade de vendas)')
    fig_vendas_vendedores.update_layout(yaxis_title = '', xaxis_title = 'Quantidade de vendas')
    st.plotly_chart(fig_vendas_vendedores, use_container_width=True)
