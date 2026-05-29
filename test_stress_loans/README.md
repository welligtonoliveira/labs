# Testes de Stress de Empréstimos (Noverde Loans Stress Test)

Este projeto implementa uma suite de testes de stress robusta utilizando **Locust** para validar a performance, confiabilidade e comportamento sob carga dos endpoints de solicitação e análise de crédito da API da Noverde.

---

## 🏗️ Arquitetura do Teste

O Locust simula múltiplos usuários simultâneos executando fluxos de empréstimo sequenciais com dependência direta de dados. Cada usuário virtual simula o seguinte comportamento:

1. **Geração de Dados Dinâmicos e Válidos:**
   Para garantir que as solicitações de empréstimo não sejam rejeitadas precocemente por validação de campos, o script possui geradores nativos de alta performance para:
   - **CPF:** Gerador de algoritmo oficial (válido).
   - **Nome Completo:** Nomes brasileiros reais combinados aleatoriamente.
   - **Data de Nascimento:** Idades realistas de adultos (18 a 65 anos) formatadas como `YYYY-MM-DD`.
   - **Email:** Limpo e baseado no nome gerado.
   - **Celular:** Formato brasileiro padrão de 11 dígitos contendo DDDs válidos e o prefixo `9`.

2. **Fluxo Sequencial Dependente:**
   - **Passo 1 (POST):** Envia uma requisição de criação de empréstimo para `/v1/loans` com o payload gerado.
   - **Passo 2 (Extração):** Captura e decodifica o identificador único `uid` retornado na resposta do POST.
   - **Passo 3 (PUT - Dependente):** Realiza uma requisição PUT para `/v1/loans/{uid}/credit-analysis` enviando o corpo vazio para iniciar a análise de crédito correspondente.

---

## 📁 Estrutura de Arquivos

Toda a estrutura está autocontida na pasta `/test_stress_loans/`:

```bash
test_stress_loans/
├── 0001_spec_initial.md    # Especificações do projeto
├── docker-compose.yml       # Orquestração do Locust via Docker
├── locustfile.py            # Definição do cenário de testes e geradores em Python
├── README.md                # Instruções completas de uso
├── requirements.txt         # Declaração das dependências Python
└── run_stress_test.sh       # Script facilitador para execução local e em container
```

---

## 🚀 Como Executar os Testes

O projeto foi desenhado priorizando a experiência **Docker-first**, eliminando a necessidade de instalar Python ou Locust diretamente no sistema host. No entanto, ambos os métodos de execução estão totalmente disponíveis.

### Opção A: Utilizando Docker (Recomendado - Sem Dependências Locais)

#### 1. Modo Web GUI (Interface Gráfica)
Sobe o Locust em segundo plano expondo a porta `8089`. Você poderá configurar o teste e visualizar relatórios gráficos dinâmicos pelo navegador.

```bash
# Executa através do script facilitador
./run_stress_test.sh --web

# OU diretamente com docker compose
docker compose up
```
Após subir o container, acesse: **[http://localhost:8089](http://localhost:8089)**

#### 2. Modo Headless (Automatizado com Geração de Relatório)
Executa o teste de stress de forma totalmente headless em background e exporta um relatório completo em HTML no final da execução.

```bash
# Executa o teste por 1 minuto com 10 usuários virtuais e taxa de subida de 2/seg
./run_stress_test.sh -u 10 -r 2 -d 1m
```

---

### Opção B: Executando Localmente (Requer Python 3.11+)

Se você preferir executar fora do Docker e possuir o ambiente Python configurado com suporte à instalação de pacotes:

1. **Crie e ative um ambiente virtual (venv):**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
   
   > [!NOTE]
   > **Nota para sistemas Debian/Ubuntu:** Caso receba um erro informando que `ensurepip` não está disponível, instale o pacote de ambiente virtual do sistema executando:
   > ```bash
   > sudo apt update && sudo apt install python3-venv
   > # ou instale para a versão exata do seu Python, ex:
   > sudo apt install python3.12-venv
   > ```
   > Se você não possuir privilégios de `sudo`, a maneira recomendada e 100% garantida é utilizar a **Opção A (Docker)**.


2. **Instale as dependências:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Execute através do script facilitador com a flag `-l`/`--local`:**
   - **Para abrir a Web GUI local:**
     ```bash
     ./run_stress_test.sh --local --web
     ```
   - **Para rodar headless localmente com relatório HTML automático:**
     ```bash
     ./run_stress_test.sh --local -u 50 -r 5 -d 5m
     ```

---

## 📊 Relatórios de Performance e Status ("Ter report com todos os status e situações")

Ao executar em modo **Headless**, o script salva automaticamente um relatório rico com o padrão de nomenclatura `report_YYYYMMDD_HHMMSS.html` dentro do diretório do projeto. Este relatório contém:

- **Estatísticas Completas:** Média, mediana, percentis (90%, 99%), throughput (RPS), sucessos e falhas detalhadas para cada endpoint (`POST` e `PUT`).
- **Detalhamento de Status:** Captura e categorização exata de falhas de rede, tempos excedidos (timeouts) e códigos de status HTTP indesejados (como `500 Internal Server Error` ou `400 Bad Request`).
- **Gráficos Dinâmicos:** Curva de evolução de usuários vs. requisições por segundo e evolução do tempo de resposta.

Você pode customizar o nome de saída do relatório com a flag `-o` ou `--output`:
```bash
./run_stress_test.sh -u 20 -r 4 -d 2m -o meu_relatorio_customizado.html
```

---

## 🛠️ Opções Completas do Script de Execução

Você pode customizar a execução passando os seguintes parâmetros para `./run_stress_test.sh`:

| Parâmetro | Descrição | Padrão |
| :--- | :--- | :--- |
| `-u, --users` | Quantidade total de usuários virtuais concorrentes | `10` |
| `-r, --rate` | Taxa de spawn (usuários por segundo) | `2` |
| `-d, --duration` | Duração do teste (ex: `30s`, `5m`, `1h`) | `1m` |
| `-h, --host` | URL base do ambiente a ser testado | `https://api.stg.noverde.com.br` |
| `-o, --output` | Nome do arquivo do relatório HTML gerado | `report_<timestamp>.html` |
| `-l, --local` | Define a execução no host local ao invés de usar Docker | *(Falso)* |
| `--web` | Roda em modo interativo com interface Web | *(Falso)* |
| `--help` | Exibe o menu de ajuda com as instruções | N/A |
