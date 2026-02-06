# Script de Callback de Desembolso

Este projeto contém um script Python para processar desembolsos enviando callbacks para a API da Moneyplus.

## Funcionalidades

- **Processamento em Lote**: Lê identificadores e propostas de um arquivo CSV (`result_query.csv`).
- **Persistência**: Mantém um registro dos IDs processados em `processed_ids.txt` para evitar duplicidade em caso de reinicialização.
- **Log de Auditoria**: Registra todas as ações e respostas da API em `audit.log`.
- **Segurança**: Utiliza variáveis de ambiente para gerenciar a API Key.

## Pré-requisitos

- Python 3.12+
- `make` (opcional, para facilitar a instalação)

## Instalação

Você pode usar o `Makefile` para configurar o ambiente virtual e instalar as dependências automaticamente:

```bash
make install-dev
```

Isso irá:
1. Criar um ambiente virtual em `.venv`.
2. Instalar as dependências do `requirements.txt`.
3. Criar um arquivo `.env` com a configuração padrão se ele não existir.

## Configuração

O arquivo `.env` deve conter a chave da API. O comando `make install-dev` cria este arquivo automaticamente, mas verifique se o conteúdo está correto:

```env
API_KEY="SUA_CHAVE_AQUI"
```

Certifique-se de que o arquivo de dados `result_query.csv` está presente na raiz do projeto.

## Execução

Para executar o script, utilize o Python do ambiente virtual:

```bash
.venv/bin/python main.py
```

Ou ative o ambiente primeiro:

```bash
source .venv/bin/activate
python main.py
```

## Logs e Verificação

- **Console**: O script exibe o progresso em tempo real.
- **`audit.log`**: Arquivo detalhado com o histórico de execuções.
- **`processed_ids.txt`**: Lista de IDs que obtiveram sucesso e não serão processados novamente.
