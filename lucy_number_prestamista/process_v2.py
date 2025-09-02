import csv

def processar_linhas(arquivo_entrada, arquivo_saida, debug=False):
    with open(arquivo_entrada, 'r') as file_in, open(arquivo_saida, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['sequence', 'number'])  # cabeçalho CSV

        for linha in file_in:
            if linha.startswith('D'):
                sequence = linha[1:4]
                number = linha[4:10]

                writer.writerow([sequence, number])

                if debug:
                    print(sequence, number)

    print(f"Arquivo '{arquivo_saida}' gerado com sucesso.")

# Exemplo de uso:
processar_linhas('input/SÉRIE_001_RANGE DOTZ.txt', 'SERIE_001_RANGE_DOTZ_001.csv')
