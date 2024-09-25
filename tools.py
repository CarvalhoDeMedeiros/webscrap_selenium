import pandas as pd
def atualizar_cpf(df_lg_unificado, df_hapvida) -> pd.DataFrame:
    """ Função responsável por atualizar o cpf do df_lg_unificado para o cpf do df_hapvida
    Args:
        df_lg_unificado (DataFrame): DataFrame unificado da LG
        df_hapvida (DataFrame): DataFrame da Hapvida

    Return:
        df_lg_unificado (DataFrame): DataFrame unificado da LG atualizado
    """
    # Percorrer as linhas do df_hapvida e df_lg_unificado
    for idx, row_hapvida in df_hapvida.iterrows():
        # Filtrar as linhas do df_lg_unificado que têm o mesmo nome_dependente e cpf igual a '00000000000'
        condicao = (df_lg_unificado['nome_dependente'] == row_hapvida['USUARIO']) & (df_lg_unificado['cpf'] == '00000000000')
        
        # Atualizar a coluna 'cpf' no df_lg_unificado
        df_lg_unificado.loc[condicao, 'cpf'] = row_hapvida['CPF_DEPENDENTE']
    
    return df_lg_unificado

def df_support_valor_hapvida() -> pd.DataFrame:
    """ função responsável por ler o arquivo Excel e criar um DataFrame
    para dar suporte ao dataframe da Hapvida
    Return:
        df_plano_saude (DataFrame): DataFrame com os dados do arquivo Excel
    """
    # Caminho para o arquivo
    caminho_arquivo = r'C:\Tetris\plano_saude\valor_plano_saude.xlsx'

    # Leitura do arquivo Excel e criação do DataFrame
    df_plano_saude = pd.read_excel(caminho_arquivo)

    return df_plano_saude

# Função para tratar valores de CPF, convertendo para número e aplicando zfill(11) quando possível
def formatar_cpf(valor) -> str:
    """ Função para tratar valores de CPF, convertendo para número e aplicando zfill(11) quando possível
    Args:
        valor (str): Valor a ser tratado
    Return:
        valor (str): Valor tratado
    """
    try:
        # Tenta converter para float e depois para int, removendo qualquer parte decimal
        return str(int(float(valor))).zfill(11)
    except (ValueError, TypeError):
        # Caso o valor não seja conversível para número, retorna o valor original ou vazio
        return ''

    # Função para preencher as colunas com base no agrupamento
def preencher_dependentes(grupo, desconto) -> pd.DataFrame:
    """ Função para preencher as colunas com base no agrupamento
    Args:
        grupo (DataFrame): DataFrame com os dados agrupados
    Return:
        grupo (DataFrame): DataFrame com as colunas preenchidas
    """
    
    # Certificar que 'VALOR EVENTO' é numérico para TITULAR
    grupo['VALOR EVENTO'] = pd.to_numeric(grupo['VALOR EVENTO'], errors='coerce')

    # Verificar se existe algum TITULAR
    if not grupo.loc[grupo['tipo_usuario'] == 'TITULAR', 'VALOR EVENTO'].empty:
        # if 'MARIA DA LUZ DE OLIVEIRA' in grupo['Nome'].values:
        #     breakpoint()  # O depurador para aqui se a condição for verdadeira

        # Encontrar o valor do 'VALOR EVENTO' onde 'tipo_usuario' é 'TITULAR'
        titular_valor_evento = grupo.loc[grupo['tipo_usuario'] == 'TITULAR', 'VALOR EVENTO'].values[0]
    
        # Verificar se o valor do titular é válido (não NaN)
        if pd.notna(titular_valor_evento):
            # Preencher os dependentes com as regras específicas
            grupo.loc[grupo['tipo_usuario'] == 'DEPENDENTE', 'DESCRIÇÃO DO EVENTO'] = 'DEP MED HAPVIDA'
            grupo.loc[grupo['tipo_usuario'] == 'DEPENDENTE', 'VALOR EVENTO'] = titular_valor_evento + desconto

    return grupo

def deletar_casados(df_geral_unificado) -> pd.DataFrame:
    """ Função para deletar linhas que contenham pessoas casadas
    Args:
        df_geral_unificado (DataFrame): DataFrame unificado da LG
    Return:
        df_geral_unificado (DataFrame): DataFrame unificado da LG atualizado
    """
    # Condição de validação para caso de pessoas casadas
    condicao_titular = df_geral_unificado['TIPO USUARIO'] == 'TITULAR'
    condicao_descricao_evento = df_geral_unificado['DESCRIÇÃO DO EVENTO'] == 'DEP MED HAPVIDA'

    # Filtrar linhas que satisfazem as condições
    linhas_para_deletar = df_geral_unificado[condicao_titular & condicao_descricao_evento]

    #Remover linhas
    df_geral_unificado = df_geral_unificado.drop(linhas_para_deletar.index)

    return df_geral_unificado