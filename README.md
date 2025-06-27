# 📊 API de Gestão de Profissionais da Saúde e Consultas Médicas

Este projeto é uma API RESTful para cadastro, gerenciamento e consulta de profissionais da saúde e suas consultas médicas. Desenvolvido com **Django + Django REST Framework**, utiliza **PostgreSQL**, **Poetry**, **Docker**, **JWT** e **GitHub Actions** para CI/CD.

---


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
`python manage.py test`
```

Todos os testes utilizam `APITestCase` do `rest_framework.test`.

---



---


## 🚀 Endpoints da API

Documentação completa disponível em:

- **Endpoints principais**:

| Método | Endpoint                            | Descrição                        		|
| ------ | ------------------------------------| -----------------------------------------------|
| GET    | `/docs/`                   	       | Documentação da aplicação com SwaggerUI  	|
| GET    | `/profissionais/`                   | Lista todos os profissionais     		|
| POST   | `/profissionais/`                   | Cadastra um novo profissional    		|
| PUT    | `/profissionais/<id>/`              | Edita um profissional existente  		|
| DELETE | `/profissionais/<id>/`              | Remove um profissional           		|
| GET    | /`consultas/`                       | Lista todos as consulta          		|
| POST   | `/consultas/`                       | Cadastra uma nova uma consulta   		|
| GET    | `/api/consultas/profissional/<id>`  | Lista consultas por profissional 		|
| POST   | `/users/register/`  		       | registro de novos usuários 	  		|
| POST   | `/users/login/`  		       | login para gerar o token de uso  dos endpoints |
| GET    | `/users/users`		       | lista todos os usuários cadastrados  		|
---


## 🚀 Uso da API

- **Autenticação**
```
# Registrar novo usuário
curl -X POST http://localhost:8000/users/register/ \
  -H "Content-Type: application/json" \
  -d '{"email": "novousuario@novousuario.com", "password": "senhasegura123"}'

# Login (obter token JWT)
curl -X POST http://localhost:8000/users/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "novousuario@novousuario.com", "password": "senhasegura123"}'
```

- **Exemplo de uso**
```
# Listar profissionais (com autenticação)
curl -X GET http://localhost:8000/profissionais/ \
  -H "Authorization: Bearer seu_token_jwt_aqui"

# Agendar consulta
curl -X POST http://localhost:8000/consultas/ \
  -H "Authorization: Bearer seu_token_jwt_aqui" \
  -H "Content-Type: application/json" \
  -d '{"profissional": 1, "nome_social_cliente": "João Silva", "data_consulta": "2023-12-15 14:30"}'
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

---

## ⚙️ CI/CD e Deploy

### Ferramentas Utilizadas

- **GitHub Actions** com workflow para:
  - Lint e testes unitários a cada push
  - Build e push da imagem Docker para Docker Hub
  - Deploy automático para servidor de staging/produção

### Ambiente de Produção

- VPS Linux (Ubuntu)
- Docker e docker-compose instalados
- Banco de dados PostgreSQL em container separado
- Scripts automatizados de deploy via SSH

```yaml
# Exemplo do CI no GitHub Actions
name: Docker CI/CD and Deploy

on:
  push:
    branches: [ main ]



jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:14
        env:
          POSTGRES_DB: postgres
          POSTGRES_USER: postgres
          POSTGRES_PASSWORD: postgres
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
    - uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.12'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest-django


    - name: Run migrations
      run: |
        python manage.py makemigrations
        python manage.py migrate

    - name: Run tests
      run: |
        python manage.py test

  docker-deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Login to Docker Hub
        uses: docker/login-action@v2
        with:
          username: ${{ secrets.DOCKER_HUB_USERNAME }}
          password: ${{ secrets.DOCKER_HUB_TOKEN }}
      
      - name: Build and push Docker image
        uses: docker/build-push-action@v4
        with:
          context: .
          push: true
          tags: ${{ secrets.DOCKER_HUB_USERNAME }}/hubname:latest
```

---

## 🪲 Erros Encontrados e Soluções

| Problema                                              | Solução                                                              |
| ----------------------------------------------------- | -------------------------------------------------------------------- |
| Erro de conexão de PostgreSQL no Docker               | Ajustado o `dockercompose` e `settings`                              |
| Utilização do JWT Token e Token Refresh               | Utilização de PyJWT e rest framework simplejwt para ajustes	       |
| Testes e deploy no GitHub Actions                     | Diversas correções e commits até chegar no resultado final           |

---

## 📊 Melhorias Futuras

- ~~Adição de autenticação com JWT (Token baseado)~~ --já adicionado
- ~~Permissões customizadas para edição e exclusão~~ -- somente usuários cadastrados podem fazer alterações.
- ~~Paginação e filtros mais robustos nos endpoints~~ --já adicionado no endpoint consultas por profissionais.
- Deploy via AWS

---

## 🧑‍💻 Autor

Desenvolvido por [Jon1nline]\
[LinkedIn](https://https://www.linkedin.com/in/jhonattan-gomes) | [GitHub](https://github.com/jon1nline)

