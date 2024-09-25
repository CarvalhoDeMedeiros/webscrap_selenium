from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait

from selenium_manipulador_df import ManipulacaoDataFrame
from landing_selenium_hapvida_extraction import HapVidaExtraction
from landing_selenium_lg_extraction import LgExtraction
from landing_selenium_lg_extraction_folha_pagamento import ExtractionFolhaPagamento
from landing_selenium_lg_extraction_dependentes import LgExtractionDependentes

class ExecutorSelenium(
        LgExtraction,
        HapVidaExtraction,
        ManipulacaoDataFrame,
        ExtractionFolhaPagamento,
        LgExtractionDependentes
        ):
    """ Classe feita para executar os scripts 
    selenium_lg_extraction e selenium_hapvida_extraction

    Args:
        LgExtraction: Classe responsável por extrair dados do site do LG
        HapVidaExtraction: Classe responsável por extrair dados do site do HapVida
    Return:
        None
    """
    def configurar_driver(self, donwload_dir):
        """Configura o driver do Chrome com as preferências necessárias.
        Args:
            download_dir (str): Caminho onde os arquivos serão salvos
        Return:
            driver (webdriver.Chrome): Instância configurada do Chrome WebDriver
        """
        # Aplicação de parâmetros do chrome option
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run in headless mode
        chrome_options.add_argument("--disable-gpu")  # Disable GPU hardware acceleration
        chrome_options.add_argument("--window-size=1920,1200")  # Set the window size
        chrome_options.add_argument("--log-level=3")  # Suppress console log messages
        chrome_options.add_argument("--disable-logging")  # Disable logging
        
        prefs = {
            "download.default_directory": donwload_dir,  # Define o caminho de download
            "download.prompt_for_download": False,  # Faz o Chrome perguntar onde salvar o arquivo
            "download.directory_upgrade": True,
            # "safebrowsing.enabled": True,  # Desabilitar avisos de segurança para downloads
        }

        chrome_options.add_experimental_option("prefs", prefs)

        driver = webdriver.Chrome(options=chrome_options)

        return driver
    def execute(self, download_dir_lg, download_dir_lg_dependentes, download_dir_folha_pagamento,download_dir_hapvida):
        """Executor dos scripts:
        1. Função que orquestra a extração de duas bases no formato CSV
        do site da LG e da Hapvida
        2. Função que orquestra a manipulação de dados no formato XLSX
        proveniente de ambos os sites
        3. Manupulação de xlsx:
            1. Manipulação de xsls do LG
            2. Manipulção de xlsx de Hapvida
            3. União de ambos os xlsx
            4. Salvar novo xlsx em pasta local

        Args:
            download_dir_lg (str): Caminho de download para os arquivos LG
            download_dir_hapvida (str): Caminho de download para os arquivos Hapvida
        Return:
            xlsx (str): arquivo xslx com os dados unidos
        """

        # ====================== parametros para extração LG =========================
        # ============================================================================
        # Configurar o WebDriver para o LG com outro diretório de download
        driver = self.configurar_driver(download_dir_lg)
        wait = WebDriverWait(driver, 20)
        # Começa a execução dos scripts para LG
        self.reprocessar_extracao(LgExtraction.extrair_lg, self, driver, wait, download_dir_lg)
        # Fechar o driver do LG
        driver.quit()

        # ====================== parametros para extração LG: Dependentes ============
        # ============================================================================
        driver = self.configurar_driver(download_dir_lg_dependentes)
        wait = WebDriverWait(driver, 20)
        # Começa a execução dos scripts para LG
        self.reprocessar_extracao(LgExtractionDependentes.extrair_lg_dependentes, self, driver, wait, download_dir_lg_dependentes)
        # Fechar o driver do LG
        driver.quit()

        # ======================= extração Folha Pagamento ===========================
        # ============================================================================
        # Configurar o WebDriver para o Folha de pagamento com outro diretório de download
        driver = self.configurar_driver(download_dir_folha_pagamento)
        wait = WebDriverWait(driver, 20)
        # Começa a execução dos scripts para Folha pagamento
        self.reprocessar_extracao(ExtractionFolhaPagamento.extracao_folha_pagamento, self, driver,wait, download_dir_folha_pagamento)
        # Fechar o driver do Folha de pagamento
        driver.quit()

        # ======================= extração Hapvida ===================================
        # ============================================================================
        # Configurar o WebDriver para o Hapvida com outro diretório de download
        driver = self.configurar_driver(download_dir_hapvida)
        wait = WebDriverWait(driver, 20)
        # Começa a execução dos scripts para Hapvida
        self.reprocessar_extracao(HapVidaExtraction.extrair_hapvida, self, driver, wait, download_dir_hapvida)
        # Fechar Driver do hapvida
        driver.quit()

        # ======================= Manipulação de dados ===================================
        # ================================================================================
        # Processo de manipulação de dados
        ManipulacaoDataFrame.execute_manipulacao_dataframe(
            self,
            download_dir_lg,
            download_dir_hapvida,
            download_dir_folha_pagamento,
            download_dir_lg_dependentes
            )

    def reprocessar_extracao(self, func, *args):
        """Função genérica para reprocessar uma função de extração em caso de falha.

        Args:
            func (callable): A função de extração a ser executada.
            *args: Argumentos posicionais a serem passados para a função de extração.
        Return:
            None
        """
        tentativas = 0
        sucesso = False
        while tentativas <= 5 and not sucesso:
            try:
                # Executa a função de extração, caso sucesso continua, caso falha tenta novamente
                func(*args)
                sucesso = True
                print(f"> {func.__name__}Concluída com sucesso.\n")

            except Exception as e:
                tentativas += 1
                print(f"> Erro ao executar função:{func.__name__} na tentativa {tentativas}: {str(e)}\n")
                if tentativas >= 5:
                    print(f"> Número máximo de tentativas atingido.\n")
                else:
                    print(f"> Tentando {func.__name__} novamente...\n")
