import tkinter as tk
from tkinter import filedialog, messagebox
import shutil
import os
import io
import sys
from PIL import Image, ImageTk 
import threading

from orquestrador_selenium import ExecutorSelenium

class RedirectStdout(io.StringIO):
# Classe para criar interface com o usuário
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget
 
    def write(self, string):
        self.text_widget.insert(tk.END, string)
        self.text_widget.see(tk.END)  # Scroll para o fim automaticamente
        self.flush()
 
    def flush(self):
        pass
class FrontPlanoSaude():
    """ Classe respponsável por criar uma interface grafica para que o usuário
        possa escolher o diretório de download dos arquivos que serão utilizados
    """

    def selecionar_arquivo(self):
        """ Função para abrir o diretório de download para o arquivo CSV
        """
        arquivo_csv = filedialog.askopenfilename(
            title="Escolha o arquivo CSV",
            filetypes=(("Arquivo CSV", "*.csv"), ("All Files", "*.*")),
        )

        if arquivo_csv:
            # Definir caminho do destino
            pasta_destino = r"C:\documentos\plano_saude\folha_pagamento"
            # Garantir que a pasta de destino existe
            if not os.path.exists(pasta_destino):
                os.makedirs(pasta_destino)
            
            # Nome do arquivo selecionado
            nome_arquivo = os.path.basename(arquivo_csv)
            # Caminho final do arquivo
            caminho_arquivo = os.path.join(pasta_destino, nome_arquivo)

            try:
                # Copiar o arquivo para a pasta de destino
                shutil.copy(arquivo_csv,caminho_arquivo)
                messagebox.showinfo("Sucesso", f"Arquivo {nome_arquivo} copiado para {pasta_destino}")
                return True
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao copiar o arquivo: {e}")
                return False
        else:
            messagebox.showinfo("Informação", "Nenhum arquivo selecionado.")
            return False
        
    def executar_orquestrador(self):
        """ Função para executar o orquestrador Selenium
        """
        def executar_selenium():
            # Inicializando o executor
            try:
                # Defina os diretórios de download para LG e Hapvida
                download_dir_ortopedia = r'C:\documentos\plano_saude\ortopedia'
                download_dir_bradesco = r'C:\documentos\plano_saude\bradesco'
                download_dir_folha_pagamento = r'C:\documentos\plano_saude\folha_pagamento'
                download_dir_dependentes = r'C:\documentos\plano_saude\ortopedia_dependentes'

                executor = ExecutorSelenium()
                executor.execute(download_dir_ortopedia, download_dir_dependentes, download_dir_folha_pagamento,download_dir_bradesco)

                print("\nFim da execução: Orquestrador executado com sucesso!\n")

            except Exception as e:
                # Exibe uma caixa de erro usando tkinter
                error_message = f"Erro ao executar o orquestrador: {e}"
                print(error_message)
                # Chama a função que abre a janela personalizada
                self.abrir_janela_erro(error_message)
        # Executar o orquestrador em uma thread separada para não bloquear a interface
        threading.Thread(target=executar_selenium).start()
    

    def salvar_e_executar(self):
        """ Função para salvar o arquivo .csv inputado pelo usuario
           e executar o orquestrador
        """
        arquivo = self.selecionar_arquivo()

        if arquivo == True:
              self.executar_orquestrador()
        else:
              messagebox.showinfo("Informação", "1.Nenhum arquivo selecionado\n 2.Extensão de arquivo inválida.")
    
    # Configurar a interface do Tkinter
    def criar_interface(self):
        """ Função para criar a interface gráfica """
        janela = tk.Tk()
        janela.title("Carregar Arquivo CSV e Executar Orquestrador")

        # Tamanho da janela
        janela.geometry("500x700")
        
        # Configurar a grid para garantir centralização
        janela.grid_columnconfigure(0, weight=1)
        janela.grid_columnconfigure(1, weight=1)
        
        # Texto de instruções
        label_instrucoes = tk.Label(janela, text="Acompanhamento da execução", font=("Times New Roman", 12))
        label_instrucoes.pack(pady=5)

        # Área de texto para mostrar saída do terminal
        self.output_text = tk.Text(janela, height=30, width=58)
        self.output_text.pack(pady=20)

        # # Verificar se está rodando em um executável ou em ambiente de desenvolvimento
        # if hasattr(sys, '_MEIPASS'):
        #     # Se for executável, use o diretório temporário onde o PyInstaller descompacta os arquivos
        #     base_path = sys._MEIPASS
        # else:
        #     # Se for no ambiente de desenvolvimento, use o diretório atual
        #     base_path = os.path.abspath(".")

        path = self.resource_path('imagem(2).png')

        try:
            # Carregar e redimensionar a imagem
            logo = Image.open(path)
            logo = logo.resize((150, 100), Image.Resampling.LANCZOS)

            # Convertendo para PhotoImage
            self.logo_img = ImageTk.PhotoImage(logo)

            # Exibe a imagem da logo na interface
            logo_label = tk.Label(janela, image=self.logo_img)
            logo_label.pack(side=tk.RIGHT, padx=10, pady=10)

        except FileNotFoundError:
            # Exibir mensagem de erro se a imagem não for encontrada
            print(f"Arquivo de imagem não encontrado: {path}")
            tk.messagebox.showerror("Erro", f"Arquivo de imagem não encontrado: {path}")

        # Redireciona o stdout do terminal para a interface do usuário
        sys.stdout = RedirectStdout(self.output_text)

        # Botão para selecionar o arquivo e executar o script
        botao_executar = tk.Button(janela, text="Executar", command=lambda: self.executar_orquestrador(), width=20)
        botao_executar.pack(side=tk.LEFT, padx=50, pady=10)

        # Iniciar o loop da interface
        janela.mainloop()

    def abrir_janela_erro(self, mensagem):
        """ Função para exibir uma janela de erro personalizada """
        erro_window = tk.Toplevel()
        erro_window.title("Erro")
        
        # Exibir a mensagem de erro
        label = tk.Label(erro_window, text=mensagem, padx=20, pady=20)
        label.pack()

        # Botão para Reiniciar o script
        botao_reiniciar = tk.Button(erro_window, text="Reiniciar", command=self.reiniciar_script, padx=10, pady=5)
        botao_reiniciar.pack(side=tk.LEFT, padx=20, pady=10)

        # Botão para Cancelar (fechar o programa)
        botao_cancelar = tk.Button(erro_window, text="Cancelar", command=self.cancelar_programa, padx=10, pady=5)
        botao_cancelar.pack(side=tk.RIGHT, padx=20, pady=10)

    def reiniciar_script(self):
        """ Função para reiniciar o script """
        try:
            # Verifica se está rodando como executável empacotado
            if getattr(sys, 'frozen', False):
                # Está rodando como um executável
                python = sys.executable  
                # Caminho do executável atual
                os.execv(python, [python] + sys.argv)  # Reinicia o executável com os mesmos argumentos
            else:
                # Está rodando em uma IDE (ambiente de desenvolvimento)
                python = sys.executable 
                # Caminho do interpretador Python
                os.execv(python, [python] + sys.argv)  
                # Reinicia o script Python na IDE
        except Exception as e:
            print(f"Erro ao reiniciar o script: {e}")

    def cancelar_programa(self):
        """ Função para fechar o programa """
        sys.exit()  # Encerra o programa

    def resource_path(self,relative_path):
        """Obtem o caminho absoluto do recurso, considerando o executável"""
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_path, relative_path)
        
# Executar a interface
if __name__ == "__main__":
    FrontPlanoSaude().criar_interface()


