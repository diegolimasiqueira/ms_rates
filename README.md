# MS Rates - Microserviço de Avaliações

Este é um microserviço desenvolvido em Python usando FastAPI e MongoDB para gerenciar avaliações de profissionais. O serviço faz parte do ecossistema EasyProFind.

## Tecnologias Utilizadas

- Python 3.12
- FastAPI 0.95.2
- MongoDB 4.7.1
- Pydantic 1.10.13
- Pytest 8.2.1
- Uvicorn
- Python-dotenv
- Mongomock (para testes)

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
MONGODB_URI=mongodb://easyprofind:securepassword@192.168.100.17:27017
```

## Executando a Aplicação

Para executar a aplicação em modo de desenvolvimento:
```bash
uvicorn src.main:app --reload
```

A API estará disponível em `http://localhost:8000`
A documentação Swagger estará disponível em `http://localhost:8000/docs`

## Endpoints

### Health Check
- `GET /health/` - Verifica a saúde do serviço

### Ratings
- `POST /ratings/` - Criar uma nova avaliação
- `GET /ratings/{rating_id}` - Buscar uma avaliação por ID
- `GET /ratings/professional/{professional_id}` - Listar avaliações de um profissional
- `GET /ratings/consumer/{consumer_id}` - Listar avaliações de um consumidor
- `DELETE /ratings/{rating_id}` - Excluir uma avaliação

## Modelo de Dados

O serviço utiliza o MongoDB para armazenar as avaliações com o seguinte schema:

```json
{
  "_id": "string (UUID)",
  "professional_id": "string (UUID)",
  "consumer_id": "string (UUID)",
  "rate": "integer (0-5)",
  "description": "string (opcional)",
  "created_at": "datetime"
}
```

## Testes

O projeto possui uma cobertura abrangente de testes:

- Testes unitários: `pytest tests/unit`
- Testes de integração: `pytest tests/integration`

Para executar todos os testes:
```bash
pytest tests/
```

## Estrutura do Projeto

```
ms_rates/
├── src/
│   ├── api/
│   │   ├── v1/
│   │   │   ├── endpoints/
│   │   │   └── schemas/
│   │   └── middleware/
│   ├── application/
│   │   ├── services/
│   │   └── dtos/
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

## Tratamento de Erros

O serviço implementa um tratamento de erros global que retorna respostas padronizadas para diferentes tipos de erros:

- Erros de validação (422)
- Erros de banco de dados (500)
- Erros de autenticação (401)
- Erros de não encontrado (404)
- Erros inesperados (500)

## Logs e Monitoramento

O serviço implementa logging estruturado para todas as operações importantes:
- Conexão com o banco de dados
- Operações CRUD
- Erros e exceções
- Eventos de startup e shutdown

## Integração

O serviço se integra com outros microserviços do ecossistema EasyProFind:
- `ms_bff`: Responsável por validar `professional_id` e `consumer_id`
- MongoDB externo: Rodando em 192.168.100.17:27017

## Observações Importantes

- O projeto é privado e não deve ser compartilhado publicamente
- As credenciais do MongoDB devem ser mantidas seguras no arquivo `.env`
- O serviço utiliza validação de schema no MongoDB para garantir a integridade dos dados
- Todos os IDs são UUIDs para garantir unicidade global
- O serviço implementa paginação para listagens de avaliações 