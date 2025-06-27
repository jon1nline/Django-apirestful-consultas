# 1. Escolhe a imagem base (Python leve)
FROM python:3.12.11

# 2. Define o diretório de trabalho dentro do container
WORKDIR /code

# 3. Instala dependências do sistema necessárias para o PostgreSQL funcionar com Python
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client=15+248 \
    curl=7.88.1-10+deb12u12 \
    && rm -rf /var/lib/apt/lists/*

# 4. Copia o arquivo de dependências para o container
COPY requirements.txt .

# 5. Instala as dependências Python no ambiente do container
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copia o restante da aplicação Django
COPY . .

# 7. Expõe a porta padrão do Django
EXPOSE 8000

# 8. Comando para rodar o servidor da aplicação
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]