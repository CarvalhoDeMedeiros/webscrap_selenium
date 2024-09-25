import pandas as pd
import os
import zipfile
import glob
import tools
import numpy as np

from selenium_manipulacao_os import ManipulacaoOs
class ManipulacaoDataFrame(ManipulacaoOs):
    """ Classe responsável por executar a manipulação dos dados
        Extraidos pelo Selenium da Hapvida e Lg
    """
    def execute_manipulacao_dataframe(self, download_dir_lg, download_dir_hapvida, download_dir_folha_pagamento, download_dir_lg_dependentes):
        """ Executa a manipulação dos dados
        Args:
            None
        Return:
        df_lg (DataFrame): Dataframe com os dados modificados
        df_hapvida (DataFrame): Dataframe com os dados modificados
        df_folha_pagamento (DataFrame): Dataframe com os dados modificados
        df_dependentes (DataFrame): Dataframe com os dados modificados

        """
        print('> TEX: Iniciando construção do xlsx\n')
        # Obtem os arquivos dos diretorios e transformar dataframe
        df_lg, df_hapvida, df_dependentes = self.obter_arquivos_lg_hapvida(download_dir_lg, download_dir_hapvida, download_dir_lg_dependentes)
        # Obtendo e manipulando arquivos csv de folha de pagamento extraido do LG
        df_pagamento = self.obtendo_e_manipulando_csv_fpagamento(download_dir_folha_pagamento)
        # Fazendo a manipulação do dataframe da remessa_hapvida
        df_hapvida, desconto = self.manipulacao_df_hapvida(df_hapvida)
        # Fazendo manipulação do dataframe LG
        df_lg, df_pagamento, df_dependentes = self.manipulacao_df_lg(df_lg, df_pagamento, df_dependentes)
        # Unificando df lg em um unico dataframe
        df_lg_unificado = self.unificador_lg(df_lg, df_pagamento, df_dependentes, desconto)
        # Unificando dataframe Hapvida com LG
        df_unificado_geral = self.unificador_hapvida_lg(df_hapvida, df_lg_unificado)


        return df_lg, df_hapvida, df_pagamento, df_dependentes
    def obter_arquivos_lg_hapvida(self, download_dir_lg, download_dir_hapvida, download_dir_lg_dependentes) -> tuple:
        """ função que obtem os arquivos das respectivas pastas para:
        1. Transformar em dataframe
        2. Manipualr os dados de ambos os dataframes
        Args:
            download_dir_lg (str): Caminho de download para os arquivos LG
            download_dir_hapvida (str): Caminho de download para os arquivos Hapvida

        Return:
            xlsx (str): arquivo xslx com os dados unidos
        """
        print('Extraindo as bases\n')
        lista_caminhos = [download_dir_lg, download_dir_hapvida, download_dir_lg_dependentes]

        for caminho in lista_caminhos:
            
            # Encontra os arquivos no diretório
            arquivo = os.listdir(caminho)
            
            if caminho == download_dir_lg:
                # Filtrar o único arquivo CSV presente
                csv_file = next((f for f in arquivo if f.endswith('.CSV')),None)
                # Abrir arquivo csv para transformar em dataframe
                caminho_csv = os.path.join(caminho, csv_file)
                df = pd.read_csv(caminho_csv, skiprows=1, sep=';', encoding='latin1')
                # Armazenando em uma variavel
                df_lg = df

            elif caminho == download_dir_hapvida:
                # Filtrar o único arquivo CSV presente
                csv_file = next((f for f in arquivo if f.endswith('.csv')),None)
                # Abrir arquivo csv para transformar em dataframe
                caminho_csv = os.path.join(caminho, csv_file)
                df = pd.read_csv(caminho_csv, sep=';', encoding='latin1')
                # Armazenando em uma variavel
                df_hapvida = df

            elif caminho == download_dir_lg_dependentes:
                # Filtrar o único arquivo CSV presente
                csv_file = next((f for f in arquivo if f.endswith('.CSV')),None)
                # Abrir arquivo csv para transformar em dataframe
                caminho_csv = os.path.join(caminho, csv_file)
                df = pd.read_csv(caminho_csv, sep=';', encoding='latin1')
                # Armazenando em uma variavel
                df_dependentes = df
                # Transformar csv em dataframe

        # Transformar em dataframe e armazenar em uma variável
        df_lg = pd.DataFrame(df_lg)
        df_hapvida = pd.DataFrame(df_hapvida)
        df_dependentes = pd.DataFrame(df_dependentes)
    
        return df_lg, df_hapvida, df_dependentes

    def obtendo_e_manipulando_csv_fpagamento(self, download_dir_folha_pagamento) -> pd.DataFrame:
        """ Função responsável por:
        1. Obter os arquivos csv de folha de pagamento extraido do LG
        2. Manipular os dados de ambos os arquivos csv
        3. Unificar os dados de ambos os arquivos csv
        Args:
            download_dir_folha_pagamento (str): Caminho de download para os arquivos Folha de pagamento
        Return:
            Dataframe (DataFrame): DataFrame com os dados unidos
        """
        print('Unificando base de pagamentos\n')
        # Inicializa uma lista para armazenar os DataFrames
        dataframes = []
        # Use glob para encontrar o arquivo .zip no diretório
        zip_files = glob.glob(os.path.join(download_dir_folha_pagamento, '*.zip'))

        # Verifica se há arquivos zip
        if zip_files:
            zip_path = zip_files[0]  # Se houver mais de um arquivo, pega o primeiro (ou ajuste a lógica conforme necessário)

        # Abre os arquivos .zip
        with zipfile.ZipFile(zip_path, 'r') as z:
            # Lista os arquivos dentro do .zip
            csv_files = [file for file in z.namelist() if file.endswith('.csv')]

            # Lista para armazenar os DataFrames
            dataframes = []

            for index, csv_file in enumerate(csv_files):  # Corrigido: csv_file em vez de csv_files
                # Lê arquivo csv dentro do .zip como um dataframe
                with z.open(csv_file) as f:  # Corrigido: csv_file em vez de csv_files
                    if index == 0:
                        # Para o primeiro arquivo csv, leia normalmente
                        df = pd.read_csv(f, sep=';', encoding='utf-8')
                    else:
                        # Para os arquivos subsequentes, leia com header=0 para ignorar o cabeçalho
                        df = pd.read_csv(f, sep=';', encoding='utf-8', header=0)
                        # Atribui as colunas do primeiro DataFrame ao novo DataFrame
                        df.columns = dataframes[0].columns

                    # Adiciona o DataFrame à lista
                    dataframes.append(df)
        # Concatenar todos os DataFrames (um embaixo do outro)
        final_df = pd.concat(dataframes, ignore_index=True)

        df_pagamento = final_df

        return df_pagamento
    
    def manipulacao_df_hapvida(self, df_hapvida) -> pd.DataFrame:
        """ Função responsável por fazer a manipulação do dataframe da Hapvida, padronizar, 
        formatar e retornar o dataframe modificado
        Args:
            df_hapvida (DataFrame): DataFrame da Hapvida
        Return:
            df_hapvida (DataFrame): DataFrame da Hapvida modificado
        """
        print('Manipulando base de dados da Hapvida\n')
        # Pegando os nomes das colunas atuais
        colunas_atuais = df_hapvida.columns.tolist()  
        # Movendo os nomes das colunas para a esquerda
        colunas_corrigidas = colunas_atuais[1:] + [None]  
        # Atribuindo as colunas corrigidas
        df_hapvida.columns = colunas_corrigidas 

        # Filtrando o DataFrame para conter apenas as colunas desejadas
        colunas_desejadas = ['CPF', 'USUARIO', 'TIPO USUARIO', 'PLANO', 'DATA PROCESSAMENTO', 'DATA CADASTRO', 'CPF_DEPENDENTE']
        df_hapvida_filtrada = df_hapvida[colunas_desejadas]

        # Atualizando df_hapvida com a versão filtrada
        df_hapvida = df_hapvida_filtrada.copy()  # Fazendo uma cópia para evitar alterações na visualização original

        # Formatar a coluna 'CPF' para ter 11 dígitos, preenchendo com zeros à esquerda
        df_hapvida['CPF'] = df_hapvida['CPF'].apply(tools.formatar_cpf)

        # Aplicar formatar_cpf e garantir que os valores válidos sejam preenchidos com zeros à esquerda
        df_hapvida['CPF_DEPENDENTE'] = df_hapvida['CPF_DEPENDENTE'].apply(
            lambda x: tools.formatar_cpf(x) if pd.notna(x) else ''
        )

        # Garantir que os valores válidos tenham 11 dígitos, preenchendo com zeros à esquerda
        df_hapvida['CPF_DEPENDENTE'] = df_hapvida['CPF_DEPENDENTE'].apply(
            lambda x: x.zfill(11) if x != '' else x
        )

        # Obter dataframe do valor do plano
        df_plano_saude = tools.df_support_valor_hapvida()
    
        # Criando um dicionário para mapear os valores de campos do df_plano_saude para o df_hapvida
        mapa_valores = df_plano_saude.set_index('categoria')['valor'].to_dict()
        df_hapvida['VALOR_PLANO'] = df_hapvida['PLANO'].map(mapa_valores)

        mapa_alojamento = df_plano_saude.set_index('categoria')['alojamento'].to_dict()
        df_hapvida['ALOJAMENTO'] = df_hapvida['PLANO'].map(mapa_alojamento)

        desconto = float(df_plano_saude['desconto'].iloc[0])

        # Percorre a coluna 'VALOR_PLANO' do DataFrame e cria uma nova coluna 'VALOR_PLANO_COM_DESCONTO' somente se TIPO USUARIO for igual a TITULAR
        df_hapvida['VALOR_PLANO_COM_DESCONTO'] = df_hapvida.apply(
            lambda row: row['VALOR_PLANO'] if row['TIPO USUARIO'] != 'TITULAR' else row['VALOR_PLANO'] - desconto, axis=1)

        return df_hapvida, desconto
    

    def manipulacao_df_lg(self, df_lg, df_pagamento, df_dependentes) -> pd.DataFrame:
        """ Função responsável por fazer a manipulação do dataframe da LG, padronizar,
        formatar e retornar o dataframe modificado
        Args:
            df_lg (DataFrame): DataFrame da LG
            df_pagamento (DataFrame): DataFrame da Folha de Pagamento
            df_dependentes (DataFrame): DataFrame dos Dependentes
        Return:
            df_lg (DataFrame): DataFrame da LG modificado
        """
        print('Manipulando base de dados da LG...\n')
        # Manipulação do dataframe da LG para filtra por colunas necessárias
        colunas_lg = ['Matrícula','Colaborador','Data Admissão','CPF/CNPJ']
        df_lg = df_lg[colunas_lg]

        df_lg = df_lg.copy()
        df_lg['CPF/CNPJ'] = df_lg['CPF/CNPJ'].str.replace(r'[.-]', '', regex=True)
        df_lg['CPF/CNPJ'] = df_lg['CPF/CNPJ'].apply(lambda x: x.zfill(11) if len(x) < 11 else x)

        df_lg['TIPO USUARIO'] = 'TITULAR'
        df_lg['CÓDIGO DEPENDENTE'] = ''
        df_lg['INICIO DA VIGÊNCIA ATUAL'] = ''
        df_lg['NOME DEPENDENTE'] = ''
        df_lg['ID DEPENDENTE'] = ''

        # Manipulação do dataframe de dependentes para filtra por colunas necessárias
        colunas_dependentes = ['MATRÍCULA COLABORADOR','CÓDIGO DEPENDENTE','COLABORADOR','INICIO DA VIGÊNCIA ATUAL','ID DEPENDENTE','NOME DEPENDENTE','CPF DEPENDENTE']
        df_dependentes = df_dependentes[colunas_dependentes]

        df_dependentes = df_dependentes.copy()
        df_dependentes['CPF DEPENDENTE'] = df_dependentes['CPF DEPENDENTE'].str.replace(r'[.-]', '', regex=True)

        # Converter todos os valores para string e garantir que NaN seja tratado como string vazia
        df_dependentes['CPF DEPENDENTE'] = df_dependentes['CPF DEPENDENTE'].apply(lambda x: str(x) if pd.notna(x) else '')
        # Preencher com zeros à esquerda os valores que têm menos de 11 caracteres
        df_dependentes['CPF DEPENDENTE'] = df_dependentes['CPF DEPENDENTE'].apply(lambda x: x.zfill(11) if len(x) < 11 else x)

        # Criando coluna Tipo_usuario
        df_dependentes['TIPO USUARIO'] = 'DEPENDENTE'
        df_dependentes['Data Admissão'] = ''


        # Manipulação do dataframe de pagamento para filtra por colunas necessárias
        colunas_pagamento = ['MATRICULA COLABORADOR','COLABORADOR','DATA DE ADMISSÃO','SITUAÇÃO','DATA INÍCIO SITUAÇÃO','CARGO','CÓDIGO DO EVENTO','DESCRIÇÃO DO EVENTO','VALOR EVENTO']
        df_pagamento = df_pagamento[colunas_pagamento]

        # Filtrar o DataFrame df_pagamento para conter apenas as linhas com os valores desejados na coluna 'DESCRIÇÃO DO EVENTO'
        # df_pagamento = df_pagamento[df_pagamento['DESCRIÇÃO DO EVENTO'].isin(['ASS MED HAPVIDA', 'DEP ASS MED HAPVIDA'])]
        df_pagamento_ass = df_pagamento[df_pagamento['DESCRIÇÃO DO EVENTO']=='ASS MED HAPVIDA']
        df_pagamento_dep = df_pagamento[df_pagamento['DESCRIÇÃO DO EVENTO']=='DEP ASS MED HAPVIDA']

        df_pagamento = pd.concat([df_pagamento_ass, df_pagamento_dep])

        return df_lg, df_dependentes, df_pagamento
    
    def unificador_lg(self, df_lg, df_dependentes, df_pagamento, desconto) -> pd.DataFrame:
        """ Função responsável por unificar o dataframe da LG, o dataframe de dependentes
        e o dataframe de pagamento, retornando o dataframe unificado
        Args:
            df_lg (DataFrame): DataFrame da LG
            df_dependentes (DataFrame): DataFrame dos Dependentes
            df_pagamento (DataFrame): DataFrame da Folha de Pagamento
        Return:
            df_unificado (DataFrame): DataFrame unificado
        """
        print('Unificando base de dados da LG e Hapvida...\n')
        # REnomeando colunas
        df_lg = df_lg.rename(columns={
            'Matrícula':'Matricula',
            'Colaborador':'Nome',
            'Data Admissão':'data_admissao',
            'CÓDIGO DEPENDENTE':'cod_dependente',
            'INICIO DA VIGÊNCIA ATUAL':'data_vigencia',
            'CPF/CNPJ':'cpf',
            'ID DEPENDENTE':'id_dependente',
            'TIPO USUARIO':'tipo_usuario',
            'NOME DEPENDENTE':'nome_dependente'
        })
        df_dependentes = df_dependentes.rename(columns={
            'MATRÍCULA COLABORADOR':'Matricula',
            'COLABORADOR':'Nome',
            'Data Admissão':'data_admissao',
            'CÓDIGO DEPENDENTE':'cod_dependente',
            'INICIO DA VIGÊNCIA ATUAL':'data_vigencia',
            'CPF DEPENDENTE':'cpf',
            'ID DEPENDENTE':'id_dependente',
            'TIPO USUARIO':'tipo_usuario',
            'NOME DEPENDENTE':'nome_dependente'
        })
        # Concatenar os dois DataFrames, colocando um em cima do outro
        df_lg_concatenado = pd.concat([df_lg, df_dependentes], ignore_index=True)

        # Adicionar uma coluna temporária para definir a ordem do tipo_usuario (TITULAR primeiro)   
        df_lg_concatenado['ordem_tipo_usuario'] = df_lg_concatenado['tipo_usuario'].apply(lambda x: 0 if x == 'TITULAR' else 1)

        # Ordenar o DataFrame resultante pela coluna 'Matrícula'
        df_lg_ordenado = df_lg_concatenado.sort_values(by=['Matricula','ordem_tipo_usuario']).reset_index(drop=True)

        # Remover a coluna temporária de ordenação
        df_lg_ordenado = df_lg_ordenado.drop(columns=['ordem_tipo_usuario'])

        # Criar coluna 'CÓDIGO DO EVENTO' 
        df_lg_ordenado['CÓDIGO DO EVENTO'] = ''
        
        df_lg_ordenado['CÓDIGO DO EVENTO'] = df_lg_ordenado['tipo_usuario'].apply(lambda x: 8110 if x == 'DEPENDENTE' else 8100)

        # Criar coluna chave_primaria para ambos os DataFrames
        df_lg_ordenado['chave_primaria'] = df_lg_ordenado['Matricula'].astype(str) + df_lg_ordenado['CÓDIGO DO EVENTO'].astype(str)
        df_pagamento['chave_primaria'] = df_pagamento['MATRICULA COLABORADOR'].astype(str) + df_pagamento['CÓDIGO DO EVENTO'].astype(str)

        # Fazendo o merge (join) entre os dois DataFrames com base na coluna 'chave_primaria'
        df_merged = df_lg_ordenado.merge(
            df_pagamento[['chave_primaria','COLABORADOR', 'DESCRIÇÃO DO EVENTO', 'VALOR EVENTO']], 
            on='chave_primaria', 
            how='right'
        )
        # Substituir vírgulas por pontos e converter para float
        df_merged['VALOR EVENTO'] = df_merged['VALOR EVENTO'].str.replace(',', '.').astype(float)

        # Aplicar o agrupamento por 'Matricula' e preencher as colunas condicionalmente
        df_merged = df_merged.groupby('Matricula', group_keys=False).apply(lambda grupo: tools.preencher_dependentes(grupo, desconto))

        df_lg_unificado = df_merged

        return df_lg_unificado

    #TODO: Unificar dataframe Hapivida com dataframe merged do LG
    def unificador_hapvida_lg(self, df_hapvida, df_lg_unificado) -> pd.DataFrame:
        """ Unificar dataframe Hapivida com dataframe merged do LG 
        e exclusão de colunas desnecessárias
            Argumentos:
                df_hapvida (DataFrame): DataFrame Hapvida
                df_lg_unificado (DataFrame): DataFrame merged do LG
            Retorna:
                df_geral_unificado (DataFrame): DataFrame unificado
        """
        # Adaptando base do LG com cpfs 00000000000
        df_lg_unificado = tools.atualizar_cpf(df_lg_unificado, df_hapvida)
        # Fazer um join por cpf retornando todas as linhas com o mesmo cpf e todas a linhas do df_hapvida
        df_geral_unificado = df_hapvida.merge(df_lg_unificado, left_on='CPF_DEPENDENTE', right_on='cpf', how='left')

        # Adicionar uma coluna temporária para definir a ordem do tipo_usuario (TITULAR primeiro)   
        df_geral_unificado['ordem_tipo_usuario'] = df_geral_unificado['TIPO USUARIO'].apply(lambda x: 0 if x == 'TITULAR' else 1)

        # Ordenar o DataFrame resultante pela coluna 'Matrícula'
        df_geral_unificado = df_geral_unificado.sort_values(by=['Matricula','ordem_tipo_usuario']).reset_index(drop=True)

        # Remover a coluna temporária de ordenação
        df_geral_unificado = df_geral_unificado.drop(columns=['ordem_tipo_usuario'])

        # Filtrando colunas do dataframe
        df_geral_unificado = df_geral_unificado.drop(['Matricula','Nome','data_admissao','cpf','tipo_usuario','cod_dependente','data_vigencia','nome_dependente','id_dependente','CÓDIGO DO EVENTO','chave_primaria','COLABORADOR'], axis=1)
        # Criando a coluna 'Status' com base na condição descrita
        df_geral_unificado['Status'] = np.where(
            (df_geral_unificado['VALOR EVENTO'].isna()) | 
            ((df_geral_unificado['VALOR EVENTO'] - df_geral_unificado['VALOR_PLANO_COM_DESCONTO']) > 1),
            'CONFERÊNCIA NECESSÁRIA',
            'VALIDADO'
        )
        # Removendo linhas que contenham pessoas casadas
        df_geral_unificado = tools.deletar_casados(df_geral_unificado)

        # Definindo caminho para salvar o arquivo
        path = r'C:\Tetris\plano_saude\plano_saude_unificado.xlsx'

        df_geral_unificado.to_excel(path, index=False)





    
