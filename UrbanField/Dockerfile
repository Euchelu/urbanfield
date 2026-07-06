# Usar imagen oficial de Python
FROM python:3.11-slim

# Evitar que Python escriba archivos .pyc y forzar salida estándar
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Directorio de trabajo en el contenedor
WORKDIR /code

# Instalar dependencias del sistema necesarias para PostgreSQL
RUN apt-get update && apt-get install -y libpq-dev gcc

# Instalar librerías de Python
COPY requirements.txt /code/
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el proyecto
COPY . /code/