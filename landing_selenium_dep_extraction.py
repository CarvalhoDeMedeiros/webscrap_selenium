from selenium.common.exceptions import NoSuchElementException,TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

from selenium_manipulacao_os import ManipulacaoOs
import os
import sys
import time
import json
class HapVidaExtraction(ManipulacaoOs):
    """ Classe responsável por extrair dados do site do L
        Encontrar os filtros, aplicar os filtros e salvar os arquivos
    Args:
        ManipulacaoOs: Classe responsável por manipular o sistema operacional
    Return:
        None
    """
    def login(self, wait):
        """ Função responsável por:"""

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
        usuario = data['credenciais_hapvida']['LOGIN']
        senha = data['credenciais_hapvida']['SENHA']

        lista_credenciais = [usuario, senha]
        lista_campos = [
            '/html/body/div[2]/div/div/form/table/tbody/tr[1]/td[2]/table/tbody/tr[1]/td[2]/input',
            '/html/body/div[2]/div/div/form/table/tbody/tr[2]/td[2]/table/tbody/tr/td[2]/input'
        ]

        for index,campo in enumerate(lista_campos):
            # Campo para inserir usuario e senha
            campo_usuario = wait.until(EC.presence_of_element_located(
                (By.XPATH,campo)
                ))
            # Clicar no campo
            campo_usuario.click()
            campo_usuario.send_keys(lista_credenciais[index])

            if index == 0:
                campo_usuario.send_keys(Keys.TAB)
            time.sleep(3)

        btn_continuar = wait.until(EC.presence_of_element_located(
            (By.XPATH,'/html/body/div[2]/div/div/form/table/tbody/tr[4]/td[2]/input[1]')
            ))
        btn_continuar.click()

    def extrair_hapvida(
        self,
        driver:object,
        wait:object,
        download_dir_bradesco:str
        ):
        """ Função responsável por:
            1. Logar no Hapvida
            2. Caminhar até a página de filtros
            3. Aplicar filtros
            4. Esperar download concluir na fila de download
            5. Salvar arquivo em local
        Args:
            driver (webdriver.Chrome): Instância configurada do Chrome WebDriver
            wait (WebDriverWait): Instância configurada do WebDriverWait
            download_dir_bradesco (str): Caminho onde os arquivos serão salvos
        Return:
            None
        """
        texto = '> Tex - iniciando extracao da Hapvida\n'
        # resultado = pyfiglet.figlet_format(texto)
        print(texto)
        # Manipula o sistema operacional para limpar os arquivos de download do LG
        # Verifica se o diretório existe e cria, se necessário
        ManipulacaoOs.verificar_ou_criar_diretorio(download_dir_bradesco)

        # Limpa o diretório se já existir
        ManipulacaoOs.limpar_diretorio(download_dir_bradesco)

        # Criar driver para sitio do LG
        driver.get("https://www.hapvida.com.br/pls/webhap/webnewcadastrousuario.login")

        # Função reponsável por fazer o login
        print('Efetuando o login na Hapvida\n')
        self.login(wait)

        time.sleep(5)

        print('Avançando entre páginas\n')

        btn_avancar = wait.until(EC.presence_of_element_located(
            (By.XPATH,'/html/body/div[2]/div/div/table[2]/tbody/tr/td/p[5]/input')
        ))
        btn_avancar.click()
        time.sleep(5)

        # Entrando na lista de serviços
        print('Entrando na lista de serviços\n')
        btn_beneficios = wait.until(EC.presence_of_element_located(
            (By.XPATH,'/html/body/div[2]/div/div/table/tbody/tr/td[1]/div/span[10]/h4')
        ))
        btn_beneficios.click()
        time.sleep(5)

        # Clicando em lista de usuários ativos
        print('Clicando em lista de usuários ativos\n')

        btn_usuarios_ativos = wait.until(EC.presence_of_element_located(
            (By.XPATH,'/html/body/div[2]/div/div/table/tbody/tr/td[1]/div/span[10]/ul/li[5]/a')
        ))
        btn_usuarios_ativos.click()
        time.sleep(5)

        # Fazendo downlaod da base de dados da hapvida
        print('Fazendo downlaod da base de dados da hapvida\n')
        btn_download = wait.until(EC.presence_of_element_located(
            (By.XPATH,'/html/body/div[2]/div/div/table/tbody/tr/td[2]/table[1]/tbody/tr[2]/td/p/strong/a/input')
        ))
        time.sleep(2)
        btn_download.click()
        time.sleep(5)

        print('Download concluído\n')