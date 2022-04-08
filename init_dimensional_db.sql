CREATE SCHEMA dimensional;
CREATE TABLE dimensional.dm_cliente (
  id_cliente INT PRIMARY KEY NOT NULL,
  nome_cliente VARCHAR(300) NOT NULL,
  status_cliente VARCHAR(8) NOT NULL CHECK (status_cliente in ('Gold', 'Silver', 'Platinum')),
  sexo_cliente CHAR(1) NOT NULL CHECK (sexo_cliente in ('M', 'F')),
  uf_cliente CHAR(2) NOT NULL CHECK (
    uf_cliente in (
      'AC',
      'AL',
      'AM',
      'AP',
      'BA',
      'CE',
      'DF',
      'ES',
      'GO',
      'MA',
      'MG',
      'MS',
      'MT',
      'PA',
      'PB',
      'PE',
      'PI',
      'PR',
      'RJ',
      'RN',
      'RO',
      'RR',
      'RS',
      'SC',
      'SE',
      'SP',
      'TO'
    )
  )
);
CREATE TABLE dimensional.dm_vendedor (
  id_vendedor INT PRIMARY KEY NOT NULL,
  nome_vendedor VARCHAR(300) NOT NULL
);
CREATE TABLE dimensional.dm_nivel_vendedor (
  id_nivel_vendedor INT PRIMARY KEY NOT NULL,
  nivel_vendedor INT NOT NULL,
  descricao_nivel_vendedor VARCHAR(300) NOT NULL
);
CREATE TABLE dimensional.dm_produto (
  id_produto INT PRIMARY KEY NOT NULL,
  nome_produto VARCHAR(300) NOT NULL,
  valor_unitario NUMERIC(10, 2)
);
CREATE TABLE dimensional.dm_classe_produto (
  id_classe_produto INT PRIMARY KEY NOT NULL,
  classe_produto VARCHAR(6) NOT NULL,
  descricao_classe_produto VARCHAR(300) NOT NULL
);
CREATE TABLE dimensional.dm_tempo (
  id_tempo INT PRIMARY KEY NOT NULL,
  data DATE NOT NULL,
  dia INT NOT NULL,
  mes INT NOT NULL,
  mes_extenso VARCHAR(15) NOT NULL,
  ano INT NOT NULL,
  trimestre CHAR(6) NOT NULL
);
CREATE TABLE dimensional.ft_vendas (
  id_cliente INT NOT NULL REFERENCES dimensional.dm_cliente ON DELETE RESTRICT ON UPDATE CASCADE,
  id_vendedor INT NOT NULL REFERENCES dimensional.dm_vendedor ON DELETE RESTRICT ON UPDATE CASCADE,
  id_nivel_vendedor INT NOT NULL REFERENCES dimensional.dm_nivel_vendedor ON DELETE RESTRICT ON UPDATE CASCADE,
  id_produto INT NOT NULL REFERENCES dimensional.dm_produto ON DELETE RESTRICT ON UPDATE CASCADE,
  id_classe_produto INT NOT NULL REFERENCES dimensional.dm_classe_produto ON DELETE RESTRICT ON UPDATE CASCADE,
  id_tempo INT NOT NULL REFERENCES dimensional.dm_tempo ON DELETE RESTRICT ON UPDATE CASCADE,
  valor_unitario NUMERIC(10, 2) NOT NULL,
  total_venda NUMERIC(10, 2) NOT NULL,
  desconto_venda NUMERIC(10, 2) NOT NULL
);