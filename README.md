# 📊 API de Gestão de Profissionais da Saúde e Consultas Médicas

Este projeto é uma API RESTful para cadastro, gerenciamento e consulta de profissionais da saúde e suas consultas médicas. Desenvolvido com **Django + Django REST Framework**, utiliza **PostgreSQL**, **Poetry**, **Docker** e **GitHub Actions** para CI/CD.

---

## 🧰 Tecnologias Utilizadas

- Python 
- Django 
- Django REST Framework
- PostgreSQL
- Poetry
- Docker & Docker Compose
- GitHub Actions

---

## ⚙️ Setup do Ambiente

### Pré-requisitos

- Docker
- Docker Compose
- Git

### Clonando o repositório

```bash
git clone https://github.com/jon1nline/Django-apirestful-consultas.git
cd Django-apirestful-consultas
```

### Inicializando com Docker

```bash
docker-compose up --build
```

A aplicação estará disponível em: [http://localhost:8000](http://localhost:8000)


## 🧪 Rodando os Testes

### Usando Docker

```bash
docker-compose up --build
```

### Localmente (sem Docker)

```bash
poetry install
poetry shell
Altere as configurações em setting para a database local
python manage.py test
```

Todos os testes utilizam `APITestCase` do `rest_framework.test`.

---

## 🚀 Endpoints da API

Documentação completa disponível em:

- **Endpoints principais**:

| Método | Endpoint                            | Descrição                        |
| ------ | ------------------------------------| -------------------------------- |
| GET    | `/profissionais/`                   | Lista todos os profissionais     |
| POST   | `/profissionais/`                   | Cadastra um novo profissional    |
| PUT    | `/profissionais/<id>/`              | Edita um profissional existente  |
| DELETE | `/profissionais/<id>/`              | Remove um profissional           |
| GET    | /`consultas/`                       | Lista todos as consulta          |
| POST   | `/consultas/`                       | Cadastra uma nova uma consulta   |
| GET    | `/api/consultas/profissional/<id>`  | Lista consultas por profissional |

---

## 🔐 Segurança e Validação

- **Prevenção de SQL Injection** com ORM do Django

---

## 🧠 Decisões Técnicas

- **Django REST Framework** foi escolhido pela robustez na criação de APIs e familiaridade com validações, autenticação e viewsets.
- **Poetry** para gestão precisa de dependências e ambientes isolados.
- **Docker** permite setup padronizado e portabilidade da aplicação.
- **PostgreSQL** pela confiabilidade e suporte ao Django.
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
| Testes e deploy no GitHub Actions                     | Diversas correções e commits até chegar no resultado final           |

---

## 📊 Melhorias Futuras

- Adição de autenticação com JWT (Token baseado)
- Permissões customizadas para edição e exclusão
- Paginação e filtros mais robustos nos endpoints
- Deploy via AWS

---

## 🧑‍💻 Autor

Desenvolvido por [Jon1nline]\
[LinkedIn](https://https://www.linkedin.com/in/jhonattan-gomes) | [GitHub](https://github.com/jon1nline)

