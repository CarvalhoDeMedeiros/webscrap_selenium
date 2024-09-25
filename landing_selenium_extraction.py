from selenium.common.exceptions import NoSuchElementException,TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from selenium_manipulacao_os import ManipulacaoOs
import json
import os
import sys
import time
import pyfiglet
class LgExtraction(ManipulacaoOs):
    """ Classe responsável por extrair dados do site do L
        Encontrar os filtros, aplicar os filtros e salvar os arquivos
    Args:
        ManipulacaoOs: Classe responsável por manipular o sistema operacional
    Return:
        None
    """

    def extrair_lg(
        self,
        driver:object,
        wait:object,
        download_dir:str
        ):
        """
        Função responsável por:
            1. Logar no LG
            2. Caminhar até a página de filtros
            3. Aplicar filtros
            4. Esperar download concluir na fila de download
            5. Salvar arquivo em local
        Args:
            driver (webdriver.Chrome): Instância configurada do Chrome WebDriver
            wait (WebDriverWait): Instância configurada do WebDriverWait
            download_dir (str): Caminho onde os arquivos serão salvos
        Return:
            None
        """

        texto = '> Tex - Iniciando extracao do LG\n'
        # resultado = pyfiglet.figlet_format(texto)
        print(texto)
        # Manipula o sistema operacional para limpar os arquivos de download do LG
        # Verifica se o diretório existe e cria, se necessário
        ManipulacaoOs.verificar_ou_criar_diretorio(download_dir)

        # Limpa o diretório se já existir
        ManipulacaoOs.limpar_diretorio(download_dir)

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
            campo_usuario_senha = wait.until(EC.presence_of_element_located(
                (By.XPATH,campo)
                ))
            # Clicar no campo
            campo_usuario_senha.click()
            time.sleep(2)
            campo_usuario_senha.send_keys(lista_credenciais[index])
            btn_continuar = wait.until(EC.presence_of_element_located(
                (By.XPATH,'/html/body/div/div[2]/div/div[2]/main/div[1]/form/div[3]/p/button')
                ))
            time.sleep(2)
            btn_continuar.click()
            time.sleep(3)

            if index == 1:
                try:
                    # Verificando a senha invalida
                    senha_invalida = driver.find_element(
                        By.XPATH,'/html/body/div/div[2]/div/div[2]/main/div[1]/form/div[2]/div[2]/div/div'
                        )
                    if senha_invalida:
                        raise Exception ('ERRO: Senha inválida! Por favor verifique se houve mudança na senha do usuário!\n')
                except NoSuchElementException:
                    # Se o elemento não for encontrado, isso significa que não houve erro de senha, então continue
                    print("Sucesso ao logar. Continuando...\n")

        print('Página do LG em carregamento\n')
        # Verificação de presença de pop up
        time.sleep(10)
        try:
            popup = wait.until(EC.presence_of_element_located(
                (By.XPATH,'/html/body/div[7]/div/div[1]')
            ))
            if popup:
                fechar = wait.until(EC.presence_of_element_located(
                    (By.XPATH,'/html/body/div[7]/div/div[1]/div/div[3]/div[3]')
                ))
                fechar.click()
        except:
            print('Nenhuma pop up encontrada! Prosseguindo...\n')

        esperando_menu = 0

        # Procurando o Botão do menu
        while esperando_menu < 10:
            try:
                time.sleep(20)
                # Clicar no menu lateral
                menu_lateral = wait.until(EC.presence_of_element_located(
                    (By.XPATH,'/html/body/div[1]/div/div[2]/header/a/i')
                ))
                menu_lateral.click()
                break
            except TimeoutException:
                print('Esperando a página carregar')
                esperando_menu += 1

        print('1.Entrando na página: Gerador de Relatórios\n')
        time.sleep(2)
        # Clicar no menu gerador de relatórios
        gerador_relatorios = wait.until(EC.presence_of_element_located(
            (By.XPATH,'/html/body/div[4]/div/div[2]/div/div[2]/ul/li[6]/a')
        ))
        gerador_relatorios.click()
        time.sleep(15)
        print('2.Esperando carregamento da página: Gerador de Relatórios\n')

        # Verifique se há um iframe e mude para ele
        iframes = driver.find_elements(By.XPATH, "/html/body/div[1]/div/div[3]/iframe")
        for iframe in iframes:
            driver.switch_to.frame(iframe)
            try:
                elemento = driver.find_element(By.XPATH, 
                        '/html/body/div[4]/div/div/div[3]/div[1]/form/div[2]/div/div/div/div[2]/input')
                if elemento:
                    print("3.Elemento encontrado no iframe!\n")
                    elemento.click()
                    time.sleep(6)
                    # Enviar elementos para o campo
                    pesquisa = 'COLA_Colaboradores_CSV'
                    # Enviando elementos para o campo
                    elemento.send_keys(pesquisa)
                    time.sleep(10)
                    print('4.Enviando parâmetros da pesquisa - COLA_Colaboradores_CSV\n')
                    # time.sleep(15)
                    # Encontrar botão e clicar
                    btn_COLA_Colaboradores_CSV = wait.until(EC.presence_of_element_located(
                        (By.XPATH,
                         '/html/body/div[12]/div[2]/div[2]/div/div[1]')
                    ))
                    # Anterior
                    btn_COLA_Colaboradores_CSV.click()
                    time.sleep(10)
                    # Esperando presença da janela de filtros
                    print('5.Enviando parâemtros de filtro - COLETIVO e EMPRESA\n')
                    janela_filtro = wait.until(EC.presence_of_element_located(
                        (By.XPATH,
                        '/html/body/div[14]')
                    ))
                    # Clicar em Filtros: Coletivo
                    time.sleep(10)
                    btn_coletivo = wait.until(EC.presence_of_element_located(
                        (By.XPATH,
                        '/html/body/div[14]/div[2]/div/div/div[4]/div/div/div[1]/div[1]/div[1]/div/div[1]/div/div/div[2]/div/div[2]/div/div[1]/div[1]/div[3]/a')
                    ))
                    btn_coletivo.click()
                    time.sleep(10)
                    # Clicar em Filtros: EMPRESA
                    btn_EMPRESA = wait.until(EC.presence_of_element_located(
                        (By.XPATH,
                        '/html/body/div[14]/div[2]/div/div/div[4]/div/div/div[1]/div[1]/div[1]/div/div[1]/div/div/div[2]/div/div[2]/div/div[3]/div/div[2]/div/div[2]/div[2]/div[1]/div[5]/div/div[2]/table/tbody/tr[6]/td[1]/input')
                    ))
                    btn_EMPRESA.click()
                    time.sleep(10)
                    # Encolher a página
                    btn_encolher_menu = wait.until(EC.presence_of_element_located(
                        (By.XPATH,
                        '/html/body/div[14]/div[2]/div/div/div[4]/div/div/div[1]/div[1]/div[1]/div/div[1]/div/div/div[2]/div/div[2]/div/div[1]/div[4]/a')
                    ))
                    btn_encolher_menu.click()
                    print('6.Clicando em EMITIR: Enviando relatorio para a fila\n') 
                    time.sleep(10)
                    btn_emitir = wait.until(EC.presence_of_element_located(
                        (By.XPATH,
                         '/html/body/div[14]/div[2]/div/div/div[8]/input')
                    ))
                    btn_emitir.click()
                    time.sleep(10)
                    # Esperando aparecimento do popUp - "Atenção!"
                    popUp = wait.until(EC.presence_of_element_located(
                        (By.XPATH,'/html/body/div[18]')
                        ))
                    # Clicando em 'OK"
                    btn_ok = wait.until(EC.presence_of_element_located(
                        (By.XPATH,'/html/body/div[18]/div[2]/div[2]/input')
                        ))
                    btn_ok.click()
                else:
                    print('Elemento não encontrado - tentando o proximo iframe\n')
            except NoSuchElementException:
                # Se não for encontrado, volte ao contexto principal e tente o próximo iframe
                driver.switch_to.default_content()

        # Volte ao contexto principal se necessário
        driver.switch_to.default_content()
        print('7.Seguindo para fila de downlaod\n')
        time.sleep(5)
        ## Entrando na lista de Donwloads
        # Clicando no menu do usuário
        btn_menu = wait.until(EC.presence_of_element_located(
            (By.XPATH,
            '/html/body/div[1]/div/div[2]/header/div[3]/div[3]/div/div/div')
        ))
        btn_menu.click()
        # Esperando menu supenso aparecer
        wait.until(EC.presence_of_element_located(
            (By.XPATH,
            '/html/body/div[1]/div/div[2]/header/div[3]/div[3]/div[2]/div')
        ))
        # Clicando em Monitor de Tarefas
        btn_monitor = wait.until(EC.presence_of_element_located(
            (By.XPATH,
            '/html/body/div[1]/div/div[2]/header/div[3]/div[3]/div[2]/div/div/div/ul/li[2]')
        ))
        btn_monitor.click()
        time.sleep(3)
        # Esperando aparecimento da janela de monitoramento
        wait.until(EC.presence_of_element_located(
            (By.XPATH,'/html/body/div[4]/div')
        ))

        # Primeiro, localize o iframe e mude o contexto para ele
        iframe = driver.find_element(By.XPATH, "/html/body/div[4]/div/div[2]/iframe")
        driver.switch_to.frame(iframe)  # Mude o contexto para o iframe

        # Verificar no Iframe
        while True:
            print('8.Procurando download na fila\n')
            # Verificando se existe algo na fila de download
            validacao_fila = 'Não existem tarefas em processamento'
            checagem_fila = wait.until(EC.presence_of_element_located(
                (By.XPATH, '/html/body/div[4]/div/div/div[3]/div[2]/div/div[2]/div/div/div[3]/div/div')
            ))
            if validacao_fila in checagem_fila.text:
                print('9.Carregamento de download finalizado. Preparando importação\n')
                break
            else:
                print('9.Carregamento de download em andamento. Aguardando...\n')
                time.sleep(20)
        time.sleep(15)
        # Após a fila de download finalizar, clique no botão para iniciar o download
        finalizados = wait.until(EC.presence_of_element_located(
            (By.XPATH, 
            '/html/body/div[4]/div/div/div[3]/div[2]/div/div[2]/div/div/div[2]/div[1]/div[3]/div[1]')
        ))
        time.sleep(10)
        finalizados.click()
        print('10.Iniciando Download\n')

        time.sleep(5)
        # Clique no ícone de download
        download = wait.until(EC.presence_of_element_located(
            (By.XPATH, 
            '/html/body/div[4]/div/div/div[3]/div[2]/div/div[2]/div/div/div[4]/div/div[1]/div[1]')
        ))
        download.click()
        time.sleep(30)
        print('11.Download Concluído\n')
        
        # Voltar ao conteúdo principal depois de terminar de interagir com o iframe
        driver.switch_to.default_content()

        


