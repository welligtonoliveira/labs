import os
import csv
import unicodedata

def remover_acentos(texto):
    nfkd = unicodedata.normalize('NFKD', texto)
    return "".join([c for c in nfkd if not unicodedata.combining(c)])

def gerar_nome_saida(nome_arquivo):
    nome_sem_extensao = os.path.splitext(nome_arquivo)[0]
    nome_sem_acentos = remover_acentos(nome_sem_extensao)
    nome_tratado = nome_sem_acentos.replace(" ", "_")
    return f"{nome_tratado}.csv"

def processar_arquivo(arquivo_entrada, arquivo_saida):
    with open(arquivo_entrada, 'r') as file_in, open(arquivo_saida, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['sequence', 'number'])  # Cabeçalho

        for linha in file_in:
            if linha.startswith('D'):
                sequence = linha[1:4]
                number = linha[4:10]
                writer.writerow([sequence, number])

def processar_todos_arquivos(input_dir='input', output_dir='output'):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for nome_arquivo in os.listdir(input_dir):
        if nome_arquivo.endswith('.txt'):
            caminho_entrada = os.path.join(input_dir, nome_arquivo)
            nome_saida = gerar_nome_saida(nome_arquivo)
            caminho_saida = os.path.join(output_dir, nome_saida)

            print(f"Processando: {nome_arquivo} → {nome_saida}")
            processar_arquivo(caminho_entrada, caminho_saida)

    print("Todos os arquivos foram processados com sucesso.")

# Executar
processar_todos_arquivos()
