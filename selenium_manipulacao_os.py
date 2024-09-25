import os
import shutil

class ManipulacaoOs():
    """ Classe para manipular o sistema operacional
        1. Verificar se o diretório existe
        2. Limpar o diretório
        3. Criar o diretório
    """
    # Diretório a ser verificado
    def verificar_ou_criar_diretorio(diretorio):
        """Verifica se o diretório existe. Se não existir, cria o diretório.
        """
        if not os.path.exists(diretorio):
            print(f"Diretório não existe. Criando: {diretorio}\n")
            os.makedirs(diretorio)
        else:
            print(f"Diretório já existe: {diretorio}\n")

    def limpar_diretorio(diretorio):
        """Verifica se há arquivos dentro do diretório. Se houver, apaga todos.
        """
        if os.listdir(diretorio):  # Verifica se o diretório contém arquivos
            print(f"Arquivos encontrados no diretório {diretorio}. Apagando todos os arquivos...\n")
            for filename in os.listdir(diretorio):
                file_path = os.path.join(diretorio, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)  # Remove o arquivo ou link simbólico
                        print(f"Arquivo {file_path} removido.\n")
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)  # Remove diretório
                        print(f"Diretório {file_path} removido.\n")
                except Exception as e:
                    print(f"Erro ao remover {file_path}: {e}\n")
        else:
            print(f"O diretório {diretorio} está vazio.\n")

