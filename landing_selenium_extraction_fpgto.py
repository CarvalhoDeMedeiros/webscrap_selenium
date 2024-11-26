from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

import time
from datetime import datetime
from dateutil.relativedelta import relativedelta
from selenium_manipulacao_os import ManipulacaoOs
import json
import os
import sys
class ExtractionFolhaPagamento(ManipulacaoOs):
    """ Classe responsável por extrair dados do site do LG
        Encontrar os filtros, aplicar os filtros e salvar os arquivos
    Args:
        ManipulacaoOs: Classe responsável por manipular o sistema operacional
    Return:
        None
    """
    def extracao_folha_pagamento(self, driver, wait, download_dir_folha_pagamento):
        """Função responsável por:
            1. Caminhar até a página de filtros
            2. Aplicar filtros
            3. Esperar download concluir na fila de download
            4. Salvar arquivo em local
        Args:
            driver (webdriver.Chrome): Instância configurada do Chrome WebDriver
            wait (WebDriverWait): Instância configurada do WebDriverWait
            download_dir_folha_pagamento (str): Caminho onde os arquivos serão salvos
        Return:
            None
        """
        texto = '> Tex - Iniciando extracao da Folha de Pagamento\n'
        # resultado = pyfiglet.figlet_format(texto)
        print(texto)
        # Verifica se o diretório existe e cria, se necessário
        ManipulacaoOs.verificar_ou_criar_diretorio(download_dir_folha_pagamento)

        # Limpa o diretório se já existir
        ManipulacaoOs.limpar_diretorio(download_dir_folha_pagamento)

        # Criar driver para sitio do LG
        driver.get("")

        # Verificar se está rodando em um executável ou em ambiente de desenvolvimento
        if hasattr(sys, '_MEIPASS'):
            # Executável: ajusta o caminho para a pasta temporária onde o PyInstaller descompacta os arquivos
            base_path = sys._MEIPASS
        else:
            # Desenvolvimento: usa o caminho atual da pasta onde o script está rodando
            base_path = os.path.abspath(".")

        # Caminho completo do config.json
        config_path = os.path.join(base_path, 'config.json')

        # Carregar o arquivo JSON com as credenciais
        with open(config_path, 'r') as f:
            data = json.load(f)

        # Definindo usuario e senha       
        usuario = data['credenciais']['LOGIN']
        senha = data['credenciais']['SENHA']

        lista_credenciais = [usuario, senha]
        lista_campos = [
            '/html/body/div/div[2]/div/div[2]/main/div[1]/form/div[2]/div/input',
            '/html/body/div/div[2]/div/div[2]/main/div[1]/form/div[2]/div[2]/div/input'
            ]

        for index,campo in enumerate(lista_campos):
            # Campo para inserir usuario es senha
            campo_usuario = wait.until(EC.presence_of_element_located(
                (By.XPATH,campo)
                ))
            # Clicar no campo
            campo_usuario.click()
            campo_usuario.send_keys(lista_credenciais[index])
            btn_continuar = wait.until(EC.presence_of_element_located(
                (By.XPATH,'/html/body/div/div[2]/div/div[2]/main/div[1]/form/div[3]/p/button')
                ))
            btn_continuar.click()
        
        print('1.Página do LG em carregamento\n')
        time.sleep(20)
        # Clicando na barra de pesquisa do LG
        barra_pesquisa = wait.until(EC.presence_of_element_located(
            (By.XPATH,'/html/body/div[1]/div/div[2]/header/div[2]/div/div[1]/input')
            ))
        barra_pesquisa.click()

        texto = 'emissão da folha de pagamento'

        # Digitar texto na barra de pesquisa
        barra_pesquisa.send_keys(texto)

        time.sleep(20)
        print("2. Navegando até página: Folha de pagamento\n")
        # Clicar no botão de pesquisa no menu suspenso
        botao_pesquisa = wait.until(EC.presence_of_element_located(
            (By.XPATH,'/html/body/div[4]/ul/li[2]/div/span')
            ))

        botao_pesquisa.click()

        time.sleep(20)
        print("3. Carregando parâmetros de filtros\n")
        # Primeiro, localize o iframe e mude o contexto para ele
        wait.until(EC.frame_to_be_available_and_switch_to_it((By.XPATH, '/html/body/div[1]/div/div[3]/iframe')))
        time.sleep(1)
        wait.until(EC.frame_to_be_available_and_switch_to_it((By.XPATH, '/html/body/div[4]/div/div[1]/iframe')))

        time.sleep(10)
        # Selecinar modelo CSV  na página de filtros
        csv = wait.until(EC.presence_of_element_located(
            (By.XPATH,'/html/body/form/span/table[2]/tbody/tr/td[6]/input')
        ))
        csv.click()

        time.sleep(10)
        original_window = driver.current_window_handle
        # Clicar no botão inserir parâmetros
        parametros = wait.until(EC.presence_of_element_located(
            (By.XPATH,'/html/body/form/span/table[2]/tbody/tr/td[12]/input[2]')
        ))
        parametros.click()
        time.sleep(20)
        all_windows = driver.window_handles
        # Alterna para a nova aba (a última na lista de identificadores)
        for window in all_windows:
            if window != original_window:
                driver.switch_to.window(window)
                break
        # Selecionar Folha e situação no pop up
        folha_situacao = wait.until(EC.presence_of_element_located(
            (By.XPATH,'/html/body/form/table/tbody/tr/td[5]')
        ))
        folha_situacao.click()
        time.sleep(5)
        print('4. Inserindo filtros de data\n')
        # Selecionar "Mensal" no dropdown
        mensal = wait.until(EC.presence_of_element_located(
            (By.XPATH,'/html/body/form/div[2]/div/select[1]/option[1]')
        ))
        mensal.click()

        # Selecionar data do mês anterior no formato "mm/yyyy"
        hoje_mes = datetime.now()
        data_ajustada = hoje_mes - relativedelta(months=1)
        # Gere a variável 'mes' no formato mm/yyyy
        mes = data_ajustada.strftime('%m/%Y')

        # Selecionar campo de data
        data = wait.until(EC.presence_of_element_located(
            (By.XPATH,'/html/body/form/div[2]/div/span[23]/input')
        ))
        # Apagar texto do campo data
        data.clear()
        time.sleep(1)
        data.click()
        time.sleep(1)
        data.send_keys(mes)
        time.sleep(1)
        # Enviar seleção de OK para a página
        ok = wait.until(EC.presence_of_element_located(
            (By.XPATH,'/html/body/form/input[8]')
        ))
        ok.click()
        time.sleep(2)

        # Armazena o identificador da aba principal
        main_window = driver.window_handles[0]

        # Depois de fechar a outra aba/janela, volte para a aba principal
        driver.switch_to.window(main_window)

        # Primeiro, localize o iframe e mude o contexto para ele
        wait.until(EC.frame_to_be_available_and_switch_to_it((By.XPATH, '/html/body/div[1]/div/div[3]/iframe')))
        time.sleep(1)
        wait.until(EC.frame_to_be_available_and_switch_to_it((By.XPATH, '/html/body/div[4]/div/div[1]/iframe')))
        print("5. Emitindo folha de pagamento\n")
        # Clicar no botão de Emitir
        botao_emitir = wait.until(EC.presence_of_element_located(
            (By.XPATH,'/html/body/form/span/table[2]/tbody/tr/td[12]/input[1]')
        ))
        botao_emitir.click()
        time.sleep(1)
        # Selecionando a opção "SIM"
        sim = wait.until(EC.presence_of_element_located(
            (By.XPATH,'/html/body/form/span/table[2]/tbody/tr/td[5]/input[1]')
        ))
        sim.click()
        time.sleep(5)
        print("6. Inciando download\n")
        carregamento = True
        while carregamento:
            concluido = 'Concluído'
            download = wait.until(EC.presence_of_element_located(
                (By.XPATH,'/html/body/form/table/tbody/tr[2]/td[6]')
            ))

            if download.text == concluido:
                baixar = wait.until(EC.presence_of_element_located(
                    (By.XPATH,'/html/body/form/table/tbody/tr[2]/td[8]/input[1]')
                ))
                baixar.click()
                time.sleep(10)
                carregamento = False
                print("Download: Folha de pagamento iniciado com sucesso!\n")
            else:
                print('Download em processamento')
                time.sleep(10)
        print("7. Download Concluído\n")
        driver.switch_to.default_content()
