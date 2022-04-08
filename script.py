# Imports
import sqlalchemy
import pandas as pd

# 1 - Extract

# Criação da engine do sql alchemy para o banco operacional.
db_connection_in = sqlalchemy.create_engine(
    'postgresql+pg8000://postgres:123456@localhost:5433/operational_db',
    client_encoding='utf8',
)

clientes_df = pd.read_sql(
    'SELECT * FROM relacional.clientes', db_connection_in
)
vendas_df = pd.read_sql('SELECT * FROM relacional.vendas', db_connection_in)
itensvenda_df = pd.read_sql(
    'SELECT * FROM relacional.itensvenda', db_connection_in
)
vendedores_df = pd.read_sql(
    'SELECT * FROM relacional.vendedores', db_connection_in
)
produtos_df = pd.read_sql(
    'SELECT * FROM relacional.produtos', db_connection_in
)

# 2 - Transform

# dm_cliente
dm_cliente_df = clientes_df.rename(
    columns={
        'idcliente': 'id_cliente',
        'cliente': 'nome_cliente',
        'estado': 'uf_cliente',
        'sexo': 'sexo_cliente',
        'status': 'status_cliente',
    },
    inplace=False,
)

# dm_vendedor
dm_vendedor_df = vendedores_df.rename(
    columns={'idvendedor': 'id_vendedor', 'nome': 'nome_vendedor'},
    inplace=False,
)

# dm_nivel_vendedor
dm_nivel_vendedor_df = pd.DataFrame(
    {
        'id_nivel_vendedor': [1, 2, 3],
        'nivel_vendedor': [1, 2, 3],
        'descricao_nivel_vendedor': [
            'até 199 mil reais',
            'entre 200 e 299 mil reais',
            'a partir de 300 mil reais',
        ],
    }
)

# dm_produto
dm_produto_df = produtos_df.rename(
    columns={
        'idproduto': 'id_produto',
        'produto': 'nome_produto',
        'preco': 'valor_unitario',
    },
    inplace=False,
)

# dm_classe_produto
dm_classe_produto_df = pd.DataFrame(
    {
        'id_classe_produto': [1, 2, 3],
        'classe_produto': ['Popular', 'Media', 'Alta'],
        'descricao_classe_produto': [
            'até R$499,99',
            'entre R$500,00 e R$2.999,99',
            'a partir de R$3.000,00',
        ],
    }
)

# dm_tempo
dm_tempo_df = pd.DataFrame()

dm_tempo_df['id_tempo'] = (
    vendas_df['data'].astype(str).str.replace('-', '')
).astype(int)
dm_tempo_df['data'] = vendas_df['data']

dm_tempo_df['ano'] = pd.DatetimeIndex(dm_tempo_df['data']).year
dm_tempo_df['mes'] = pd.DatetimeIndex(dm_tempo_df['data']).month
dm_tempo_df['dia'] = pd.DatetimeIndex(dm_tempo_df['data']).day

dm_tempo_df['mes_extenso'] = pd.DatetimeIndex(dm_tempo_df['data']).month
dm_tempo_df['mes_extenso'] = dm_tempo_df['mes_extenso'].replace(1, 'Janeiro')
dm_tempo_df['mes_extenso'] = dm_tempo_df['mes_extenso'].replace(2, 'Fevereiro')
dm_tempo_df['mes_extenso'] = dm_tempo_df['mes_extenso'].replace(3, 'Março')
dm_tempo_df['mes_extenso'] = dm_tempo_df['mes_extenso'].replace(4, 'Abril')
dm_tempo_df['mes_extenso'] = dm_tempo_df['mes_extenso'].replace(5, 'Maio')
dm_tempo_df['mes_extenso'] = dm_tempo_df['mes_extenso'].replace(6, 'Junho')
dm_tempo_df['mes_extenso'] = dm_tempo_df['mes_extenso'].replace(7, 'Julho')
dm_tempo_df['mes_extenso'] = dm_tempo_df['mes_extenso'].replace(8, 'Agosto')
dm_tempo_df['mes_extenso'] = dm_tempo_df['mes_extenso'].replace(9, 'Setembro')
dm_tempo_df['mes_extenso'] = dm_tempo_df['mes_extenso'].replace(10, 'Outubro')
dm_tempo_df['mes_extenso'] = dm_tempo_df['mes_extenso'].replace(11, 'Novembro')
dm_tempo_df['mes_extenso'] = dm_tempo_df['mes_extenso'].replace(12, 'Dezembro')

dm_tempo_df['trimestre_aux'] = pd.DatetimeIndex(dm_tempo_df['data']).month
dm_tempo_df['trimestre_aux'] = pd.cut(
    dm_tempo_df['trimestre_aux'],
    bins=[1, 4, 7, 10, float('inf')],
    right=False,
    labels=[1, 2, 3, 4],
)


dm_tempo_df['trimestre'] = (
    dm_tempo_df['ano'].astype(str)
    + '/'
    + dm_tempo_df['trimestre_aux'].astype(str)
)
dm_tempo_df.drop(columns=['trimestre_aux'], inplace=True)

dm_tempo_df.drop_duplicates(inplace=True)

# ft_vendas
ft_vendas_df = pd.merge(
    left=vendas_df, right=itensvenda_df, how='left', on='idvenda'
)

ft_vendas_df.rename(
    columns={
        'idcliente': 'id_cliente',
        'idvendedor': 'id_vendedor',
        'idproduto': 'id_produto',
        'idproduto': 'id_produto',
        'desconto': 'desconto_venda',
        'valorunitario': 'valor_unitario',
        'total': 'total_venda',
    },
    inplace=True,
)

ft_vendas_df['id_tempo'] = (
    ft_vendas_df['data'].astype(str).str.replace('-', '')
).astype(int)


def get_classe_produto(valor_produto):
    lista = []
    for valor in valor_produto:
        if valor <= 499.99:
            lista.append(1)
        elif valor <= 2999.99:
            lista.append(2)
        else:
            lista.append(3)
    return lista


ft_vendas_df['id_classe_produto'] = get_classe_produto(
    ft_vendas_df['valor_unitario']
)

aux_df = pd.DataFrame()
aux_df['id_vendedor'] = ft_vendas_df['id_vendedor']
aux_df['id_venda'] = ft_vendas_df['idvenda']
aux_df['total_venda'] = ft_vendas_df['total_venda']
aux_df.drop_duplicates(inplace=True)

aux_df = aux_df.groupby(['id_vendedor'])['total_venda'].agg('sum')


def get_nivel_vendedor(id_vendedor):
    lista = []
    for item in id_vendedor:
        total_vendido = aux_df[item]
        if total_vendido <= 199999:
            lista.append(1)
        elif total_vendido <= 299999:
            lista.append(2)
        else:
            lista.append(3)
    return lista


ft_vendas_df['id_nivel_vendedor'] = get_nivel_vendedor(
    ft_vendas_df['id_vendedor']
)

ft_vendas_df.drop(
    columns=['idvenda', 'valortotal', 'quantidade', 'data'],
    inplace=True,
)

# 3 - Load

# Criação da engine do sql alchemy para o banco dimensional.
db_connection_out = sqlalchemy.create_engine(
    'postgresql+pg8000://postgres:123456@localhost:5434/dimensional_db',
    client_encoding='utf8',
)

# Função para calculo do chunksize
def get_chunksize(table_columns):
    cs = 2097 // len(table_columns)
    cs = 1000 if cs > 1000 else cs
    return cs


# Exportação do dataframe dm_cliente_df do pandas para a tabela dm_cliente
dm_cliente_df.to_sql(
    name='dm_cliente',
    schema='dimensional',
    con=db_connection_out,
    index=False,
    if_exists='replace',
    chunksize=get_chunksize(dm_cliente_df.columns),
)

# Exportação do dataframe dm_vendedor_df do pandas para a tabela dm_vendedor
dm_vendedor_df.to_sql(
    name='dm_vendedor',
    schema='dimensional',
    con=db_connection_out,
    index=False,
    if_exists='replace',
    chunksize=get_chunksize(dm_vendedor_df.columns),
)

# Exportação do dataframe dm_nivel_vendedor_df do pandas para a tabela dm_nivel_vendedor
dm_nivel_vendedor_df.to_sql(
    name='dm_nivel_vendedor',
    schema='dimensional',
    con=db_connection_out,
    index=False,
    if_exists='replace',
    chunksize=get_chunksize(dm_nivel_vendedor_df.columns),
)

# Exportação do dataframe dm_produto_df do pandas para a tabela dm_produto
dm_produto_df.to_sql(
    name='dm_produto',
    schema='dimensional',
    con=db_connection_out,
    index=False,
    if_exists='replace',
    chunksize=get_chunksize(dm_produto_df.columns),
)

# Exportação do dataframe dm_classe_produto_df do pandas para a tabela dm_classe_produto
dm_classe_produto_df.to_sql(
    name='dm_classe_produto',
    schema='dimensional',
    con=db_connection_out,
    index=False,
    if_exists='replace',
    chunksize=get_chunksize(dm_classe_produto_df.columns),
)

# Exportação do dataframe dm_tempo_df do pandas para a tabela dm_tempo
dm_tempo_df.to_sql(
    name='dm_tempo',
    schema='dimensional',
    con=db_connection_out,
    index=False,
    if_exists='replace',
    chunksize=get_chunksize(dm_tempo_df.columns),
)

# Exportação do dataframe ft_vendas_df do pandas para a tabela ft_vendas
ft_vendas_df.to_sql(
    name='ft_vendas',
    schema='dimensional',
    con=db_connection_out,
    index=False,
    if_exists='replace',
    chunksize=get_chunksize(ft_vendas_df.columns),
)
