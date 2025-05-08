# MS Rates - Microserviço de Avaliações

Este é um microserviço desenvolvido em Python usando FastAPI e MongoDB para gerenciar avaliações de profissionais.

## Tecnologias Utilizadas

- Python 3.12
- FastAPI 0.95.2
- MongoDB 4.7.1
- Pydantic 1.10.13
- Pytest 8.2.1

## Requisitos

- Python 3.12 ou superior
- MongoDB
- Ambiente virtual Python (venv)

## Arquitetura

O projeto segue os princípios da Arquitetura Hexagonal (Ports and Adapters) e Clean Architecture, dividido em camadas:

- **API Layer**: Contém os endpoints e schemas da API
- **Application Layer**: Contém a lógica de negócio e serviços
- **Domain Layer**: Contém as entidades, interfaces e regras de negócio
- **Infrastructure Layer**: Contém implementações concretas (repositórios, banco de dados)

## Configuração do Ambiente

1. Clone o repositório:
```bash
git clone <repository_url>
cd ms_rates
```

2. Crie e ative o ambiente virtual:
```bash
python3.12 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
.\venv\Scripts\activate  # Windows
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Configure as variáveis de ambiente:
Crie um arquivo `.env` na raiz do projeto com o seguinte conteúdo:
```env
MONGODB_URI=mongodb://localhost:27017/easyprofind
MONGODB_DATABASE=easyprofind
MONGODB_COLLECTION=ratings
```

5. (Opcional) Para desenvolvimento local, você pode usar Docker para o MongoDB:
```bash
docker run -d -p 27017:27017 --name mongodb mongo:4.7.1
```

## Executando a Aplicação

Para executar a aplicação em modo de desenvolvimento:
```bash
uvicorn src.main:app --reload
```

A API estará disponível em `http://localhost:8000`
A documentação Swagger estará disponível em `http://localhost:8000/docs`

## Endpoints

### Ratings

- `POST /ratings/` - Criar uma nova avaliação
- `GET /ratings/{rating_id}` - Buscar uma avaliação por ID
- `GET /ratings/professional/{professional_id}` - Listar avaliações de um profissional

## Testes

Para executar os testes:
```bash
pytest tests/
```

## Estrutura do Projeto

```
ms_rates/
├── src/
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/
│   │       └── schemas/
│   ├── application/
│   │   └── services/
│   ├── domain/
│   │   ├── interfaces/
│   │   └── exceptions/
│   └── infrastructure/
│       ├── database/
│       └── repositories/
├── tests/
│   ├── integration/
│   └── unit/
├── .env
├── requirements.txt
└── README.md
```

## Descrição
O `ms_rate` é responsável por gerenciar avaliações de profissionais feitas por consumidores. Utiliza FastAPI, MongoDB e segue princípios de clean code e arquitetura de microserviços.

## Estrutura do Projeto
```
ms_rate/
├── src/
│   ├── api/
│   │   ├── v1/
│   │   │   ├── endpoints/
│   │   │   └── schemas/
│   │   │
│   │   └── application/
│   │       ├── services/
│   │       └── dtos/
│   │
│   ├── domain/
│   │   ├── entities/
│   │   ├── interfaces/
│   │   └── value_objects/
│   │
│   ├── infrastructure/
│   │   ├── database/
│   │   ├── repositories/
│   │   └── external/
│   │
│   └── main.py
│
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
│
├── Dockerfile
│
├── requirements.txt
│
├── .env
│
├── .gitignore
│
└── README.md
```

## Requisitos
- Python 3.10+
- FastAPI
- PyMongo
- Pydantic
- python-dotenv
- pytest
- mongomock (para testes)
- MongoDB (externo, já rodando em 192.168.100.17:27017)

## Configuração
1. Clone o repositório e acesse o diretório `ms_rate`.
2. Crie um arquivo `.env` com:
   ```
   MONGODB_URI=mongodb://easyprofind:securepassword@192.168.100.17:27017
   ```
3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

## Rodando Localmente
```bash
uvicorn src.main:app --reload
```

## Rodando com Docker
```bash
docker build -t ms_rate .
docker run --env-file .env -p 8000:8000 ms_rate
```

## API Documentation
O microserviço inclui documentação automática via Swagger UI e ReDoc:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

A documentação inclui:
- Descrição detalhada de todos os endpoints
- Schemas de requisição e resposta
- Exemplos de uso
- Códigos de erro possíveis

## Endpoints
- `GET /health`: Health check do serviço
- `POST /ratings`: Cria uma avaliação
- `GET /ratings/{id}`: Busca avaliação por ID
- `GET /ratings/professional/{professional_id}`: Lista avaliações de um profissional

## Integração com ms_bff
O `ms_bff` é responsável por validar `professional_id` e `consumer_id` antes de chamar o `ms_rate`.

## Observações
- Não há pasta `migrations` (MongoDB é schemaless).
- Não há `docker-compose.yml` (MongoDB já está rodando externamente).
- A coleção `ratings` é inicializada com validação de esquema ao iniciar o app.
- Logs são gerados para todas as operações importantes.
- Erros são tratados e retornados com códigos HTTP apropriados.

## Testes
- Testes unitários: `pytest tests/unit`
- Testes de integração: `pytest tests/integration`
- Os testes de integração usam `mongomock` para simular o MongoDB.

## Modelo de Dados

O serviço utiliza o MongoDB para armazenar as avaliações com o seguinte schema:

```json
{
  "professional_id": "string",
  "consumer_id": "string",
  "rating": number,
  "comment": "string",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

## Logs e Monitoramento

O serviço implementa logging estruturado para todas as operações importantes:
- Criação de avaliações
- Busca de avaliações
- Erros e exceções
- Operações de banco de dados

Os logs são formatados em JSON para fácil integração com ferramentas de monitoramento. 