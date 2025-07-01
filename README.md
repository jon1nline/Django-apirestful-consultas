# 📊 API de Gestão de Profissionais da Saúde e Consultas Médicas

Este projeto é uma **API RESTful** completa para cadastro, agendamento, gerenciamento e pagamentos de consultas médicas. A solução inclui um **CRUD** de profissionais, agendamento de consultas e uma integração robusta com a **Asaas** para processamento de pagamentos.

Desenvolvido com **Django** + **Django REST Framework**, utiliza **PostgreSQL** para o banco de dados, **Poetry** para gerenciamento de dependências, e é totalmente containerizado com **Docker**. O fluxo de **CI/CD** é automatizado com GitHub Actions para testes e deploy na nuvem **AWS**.

---

## ✨ Principais Funcionalidades

*CRUD de Profissionais*: Cadastro, visualização, atualização e remoção de profissionais da saúde.

*Gerenciamento de Consultas*: Agendamento e listagem de consultas por data ou profissional.

*Gerenciamento de Clientes*: Cadastro de novos clientes e listagem de todos os clientes cadastrados.

*Autenticação e Autorização*: Sistema de registro e login de usuários com tokens JWT, protegendo os endpoints.

*Integração de Pagamentos com Asaas:*

Criação de clientes na plataforma Asaas: Ao cadastrar um novo cliente, os dados são automaticamente enviados para o cadastro no sistema Asaas

Geração de cobranças (PIX, boleto, cartão) para as consultas: Ao registrar novas consultas, automaticamente é criado o registo de pagamento no sistema Asaas.

Recebimento de atualizações de status de pagamento via webhooks: Ao pagamento ser registrado, o sistema Asaas envia um webhook a API para que haja a atualização do status do pagamento e da consulta.

**CI/CD**: Pipeline automatizado para testes e deploy contínuo na AWS.


## ⚙️ Setup do Ambientes

### Pré-requisitos

- Docker
- Git
- Python 
- Django 
- PostgreSQL
- Poetry

### Clonando o repositório

```bash
git clone https://github.com/jon1nline/Django-apirestful-consultas.git
cd Django-apirestful-consultas
```

### Instalação com Docker(Recomendado)

```
# Crie e inicie os containers
docker-compose up --build

# Para parar os containers
docker-compose down

# Para reiniciar
docker-compose restart
```
A aplicação estará disponível em: [http://localhost:8000](http://localhost:8000)

### Instalação local
```
# Instale as dependências com Poetry
poetry install

# Instale dependências adicionais
`Linux/Mac
cat requirements.txt | xargs poetry add`

`Windows (PowerShell)
Get-Content requirements.txt | ForEach-Object { poetry add $_ }`

# Configure o banco de dados (edite settings.py)
Edite as configurações em lacreisaude/settings.py

# Execute as migrações
python manage.py migrate

# Inicie o servidor
python manage.py runserver
```

## 🧪 Rodando os Testes

### Usando Docker

```bash
docker-compose up --build
```

### testando localmente (sem Docker)

```
python manage.py test
```

Todos os testes utilizam `APITestCase` do `rest_framework.test`.

---

## 🚀 Endpoints da API

Documentação completa disponível em:

- **Endpoints principais**:

| Método | Endpoint                            		 | Descrição                        					|
| ------ | --------------------------------------------- | ---------------------------------------------------------------------|
| GET    | `/profissionais/`                   		 | Lista todos os profissionais     					|
| POST   | `/profissionais/`                   		 | Cadastra um novo profissional    					|
| PUT    | `/profissionais/<id>/`              		 | Edita um profissional existente  					|
| DELETE | `/profissionais/<id>/`              		 | Remove um profissional           					|
| GET    | `/consultas/`                       		 | Lista todas as consultas          					|
| POST   | `/consultas/`                       		 | Cadastra uma nova consulta   					|
| GET    | `/api/consultas/profissional/<id>/` 		 | Lista consultas por profissional 					|
| POST   | `/users/register/`  		       		 | Registro de novos usuários 	  					|
| POST   | `/users/login/`  		       		 | Login para gerar o token JWT     	        			|
| GET    | `/users/users/`		       		 | Lista todos os usuários cadastrados					|
| POST   | `/clients/cadastro/`  	      		 | Cadastra um novo cliente   	  	        			|
| GET    | `/clients/cadastro/`		       		 | Lista todos os clientes cadastrados					|
| PATCH  | `/clients/consultas/gerenciarpagamento/`	 | endpoint especifico Asaas para receber confirmação de pagamento	|

---

## 🚀 Uso da API

- **Autenticação**
```
# Registrar novo usuário
curl -X POST http://localhost:8000/users/register/   -H "Content-Type: application/json"   -d '{"email": "novousuario@novousuario.com", "password": "senhasegura123"}'

# Login (obter token JWT)
curl -X POST http://localhost:8000/users/login/   -H "Content-Type: application/json"   -d '{"email": "novousuario@novousuario.com", "password": "senhasegura123"}'
```

- **Exemplo de uso**
```
# Listar profissionais (com autenticação)
curl -X GET http://localhost:8000/profissionais/   -H "Authorization: Bearer seu_token_jwt_aqui"

# Agendar consulta
curl -X POST http://localhost:8000/consultas/   -H "Authorization: Bearer seu_token_jwt_aqui"   -H "Content-Type: application/json"   -d '{"profissional": 1, "cliente": "1", "data_consulta": "2023-12-15 14:30", "metodo_pagamento": "PIX"}'
```

## 🔐 Segurança e Validação

- **Prevenção de SQL Injection** com ORM do Django
- **Login e utilização de JWT Token** para proteção de endpoints

---

## 🧠 Decisões Técnicas

- **Django REST Framework** foi escolhido pela robustez na criação de APIs e familiaridade com validações, autenticação e viewsets.
- **Poetry** para gestão precisa de dependências e ambientes isolados.
- **Docker** permite setup padronizado e portabilidade da aplicação.
- **PostgreSQL** pela confiabilidade e suporte ao Django.
- **JWT** para segurança dos endpoints da aplicação.
- **GitHub Actions** para garantir CI/CD automatizado com execução de testes e deploy automatizado para produção.
- **AWS** para deploy automático na instancia EC2

---


### 🚀 CI/CD e Deploy na AWS (EC2)

1. O fluxo de CI/CD é configurado para, a cada push na branch main:

2. Executar testes e lint.

3. Construir uma nova imagem Docker.

4. Enviar a imagem para o Docker Hub.

5. Conectar-se via SSH à instância EC2 e realizar o deploy da nova versão.

#### Pré-requisitos:

- Instância EC2 (Linux Ubuntu) configurada e com Docker instalado
- Chave SSH configurada nos **Secrets do GitHub** (`EC2_HOST`, `EC2_USER`, `EC2_KEY`)
- Repositório com workflow GitHub Actions configurado

#### Variáveis de ambiente necessárias no GitHub Secrets:

| Nome                 | Descrição                                         |
|----------------------|---------------------------------------------------|
| `SSH_HOST`           | Endereço IP público da instância EC2              |
| `SSH_USER`           | Usuário SSH (ex: `ubuntu`)                        |
| `SSH_PRIVATE_KEY`    | Chave privada `.pem` convertida em string         |
| `DOCKER_HUB_USERNAME`| Usuário do Docker Hub                             |
| `DOCKER_HUB_TOKEN`   | Token de acesso ao Docker Hub                     |
| `POSTGRES_DB`        | Nome do banco de dados                            |
| `POSTGRES_HOST`      | host do banco de dados (ex:127.0.0.)              |
| `POSTGRES_PASSWORD`  | senha do banco de dados                           |
| `POSTGRES_PORT`      | porta do banco de dados(padrão:5432)          	   |
| `ASAAS_ACCESS_TOKEN` | coloque a chave Asaas para integração      	   |
| `ASAAS_WEBHOOK_TOKEN`| essa chave deve ser a mesma inserida nos webhooks |


#### Exemplo de trecho do Workflow GitHub Actions (com deploy para EC2):

```yaml
  deploy-aws:
    needs: docker-deploy
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to AWS EC2
        uses: appleboy/ssh-action@v1.0.0
        with:
          host: ${{ secrets.SSH_HOST }}
          username: ${{ secrets.SSH_USER }}
          key: ${{ secrets.SSH_PRIVATE_KEY }}
          script: |
            docker pull ${{ secrets.DOCKER_HUB_USERNAME }}/hubname:latest
            docker stop app || true && docker rm app || true
            docker run -d --name app -p 80:8000 ${{ secrets.DOCKER_HUB_USERNAME }}/hubname:latest
```

---

[DEPLOY NA AWS](http://18.223.159.22/) <- disponível nesse link

## 🪲 Erros Encontrados e Soluções

| Problema                                              | Solução                                                              |
| ----------------------------------------------------- | -------------------------------------------------------------------- |
| Erro de conexão de PostgreSQL no Docker               | Ajustado o `dockercompose` e `settings`                              |
| Utilização do JWT Token e Token Refresh               | Utilização de PyJWT e rest framework simplejwt para ajustes	       |
| Testes e deploy no GitHub Actions                     | Diversas correções e commits até chegar no resultado final           |
| Testes e deploy na instancia EC2                      | Diversas correções e commits até que o deploy fosse automatizado     |


---

## 📊 Melhorias Futuras

- ~~Adição de autenticação com JWT (Token baseado)~~ --já adicionado
- ~~Permissões customizadas para edição e exclusão~~ -- somente usuários cadastrados podem fazer alterações.
- ~~Paginação e filtros mais robustos nos endpoints~~ --já adicionado no endpoint consultas por profissionais.
- ~~Deploy na AWS~~ disponível em: http://18.223.159.22/
- ~~Integração com API Asaas~~ integração concluída com sucesso.

---

## 🧑‍💻 Autor

Desenvolvido por [Jon1nline]  
[LinkedIn](https://www.linkedin.com/in/jhonattan-gomes) | [GitHub](https://github.com/jon1nline)