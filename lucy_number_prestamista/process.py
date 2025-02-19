import psycopg2
import random
import env

def gerar_numero_aleatorio_6_digitos():
    primeiro_digito = random.randint(1, 9)
    resto_do_numero = random.randint(0, 99999)

    numero_aleatorio = f"{primeiro_digito}{resto_do_numero:05d}"
    return numero_aleatorio

def inserir_lucky_number(cursor, sequence, number):
    try:
        cursor.execute("INSERT INTO lucky_numbers (sequence, number) VALUES (%s, %s)", (sequence, number))
    except Exception as e:
        print(f"Erro ao inserir dados: {e}")

def processar_linhas(cnx_db, arquivo, fake_number=None):
    try:
        conn = psycopg2.connect(**cnx_db)
        cursor = conn.cursor()
    except Exception as e:
        print(f"Erro -->>>>: {e}")

    count = 0
    with open(arquivo, 'r') as file:
        for linha in file:
            count += 1
            if linha.startswith('D'):
                sequence = linha[1:4]
                number = linha[4:10]
                
                if fake_number:
                    sequence = '002'
                    number = gerar_numero_aleatorio_6_digitos()
                
                print(sequence, " - ", number)

                inserir_lucky_number(cursor, sequence, number)
                
                if count > 100:
                    print("Commit")
                    conn.commit()
                    count = 0
    
    conn.commit()
    cursor.close()
    conn.close()


# processar_linhas(env.DB_DEV, 'RTPD07022025_Dotz_Homolog.txt', fake_number=True)
processar_linhas(env.DB_STG, 'RTPD07022025_Dotz_Homolog.txt')
