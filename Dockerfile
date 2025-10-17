# Використовуємо офіційний легкий образ Python
FROM python:3.10-slim

# Встановлюємо змінні середовища
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# РЯДОК, ЯКИЙ ТРЕБА ВИДАЛИТИ
# RUN apt-get update && apt-get install -y build-essential default-libmysqlclient-dev

# Встановлюємо робочу директорію всередині контейнера
WORKDIR /app

# Копіюємо файл залежностей та встановлюємо їх
COPY requirements.txt .
RUN pip install -r requirements.txt

# Копіюємо весь код проєкту в робочу директорію
COPY . .